from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from employees.models import EmployeeProfile
from employers.models import EmployerProfile
from jobs.models import Job
from core.models import Skill
from accounts.models import CustomUser
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt # Needed for style and dates/ticker locators often reside here
import pandas as pd
import numpy as np
import io
import base64

class HomeView(TemplateView):
    template_name = 'core/home.html'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_plot_image(self, fig):
        canvas = FigureCanvas(fig)
        buffer = io.BytesIO()
        canvas.print_png(buffer)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png).decode('utf-8')
        return graphic

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Set chart style globally for consistency (thread-safe enough for style)
        plt.style.use('ggplot')
        
        # Common context
        context['total_employees'] = EmployeeProfile.objects.count()
        context['total_employers'] = EmployerProfile.objects.count()
        context['total_jobs'] = Job.objects.count()
        total_taken = Job.objects.filter(filled_by__isnull=False).count()
        context['total_taken'] = total_taken
        context['top_skills'] = Skill.objects.annotate(job_count=Count('job')).order_by('-job_count')[:5]
        
        # --- Charts ---
        
        # 1. System Overview (Bar Chart)
        data = {
            'Category': ['Employees', 'Employers', 'Jobs Posted', 'Jobs Taken'],
            'Count': [context['total_employees'], context['total_employers'], context['total_jobs'], total_taken]
        }
        df_overview = pd.DataFrame(data)
        
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        bars = ax.bar(df_overview['Category'], df_overview['Count'], color=['#3498db', '#2ecc71', '#f1c40f', '#e74c3c'])
        ax.set_title('System Overview')
        ax.set_ylabel('Count')
        ax.bar_label(bars, padding=3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        context['chart_overview'] = self.get_plot_image(fig)

        # 2. Top Skills in Demand (Bar Chart)
        # Fetch all required skills from jobs - using Pandas for aggregation
        job_skills = Job.objects.all().values_list('required_skills__name', flat=True)
        if job_skills:
            df_skills = pd.DataFrame(list(job_skills), columns=['Skill'])
            df_skills = df_skills.dropna() # Remove None if any
            # Group by skill and count using Pandas
            skill_counts = df_skills['Skill'].value_counts().reset_index()
            skill_counts.columns = ['Skill', 'Job Count']
            skill_counts = skill_counts.head(7) # Top 7
            skill_counts = skill_counts.sort_values('Job Count', ascending=True) # Sort for horizontal bar
            
            fig = Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            bars = ax.barh(skill_counts['Skill'], skill_counts['Job Count'], color='#9b59b6')
            ax.set_title('Top Skills in Demand')
            ax.set_xlabel('Number of Jobs')
            ax.bar_label(bars, padding=3)
            fig.tight_layout()
            context['chart_skills'] = self.get_plot_image(fig)
        else:
            context['chart_skills'] = None

        # 3. Match Quality Distribution (Pie Chart)
        filled_jobs = Job.objects.filter(filled_by__isnull=False).select_related('filled_by')
        match_scores = []
        for job in filled_jobs:
            employee = job.filled_by
            if not employee: continue
            
            # Use sets for skill comparison
            employee_skills = set(employee.skills.all())
            job_skills = set(job.required_skills.all())
            
            if not job_skills:
                skill_match = 100
            else:
                matching_skills = employee_skills.intersection(job_skills)
                skill_match = (len(matching_skills) / len(job_skills)) * 100
            
            if employee.experience_years >= job.experience_required:
                exp_match = 100
            else:
                if job.experience_required > 0:
                    exp_match = (employee.experience_years / job.experience_required) * 100
                else:
                    exp_match = 100
            
            total_score = (skill_match * 0.7) + (exp_match * 0.3)
            match_scores.append(total_score)
        
        match_scores = np.array(match_scores)
        high = np.sum((match_scores >= 70))
        medium = np.sum((match_scores >= 40) & (match_scores < 70))
        low = np.sum((match_scores < 40))
        
        if len(match_scores) > 0:
            labels = ['High Match (70-100%)', 'Medium Match (40-69%)', 'Low Match (<40%)']
            sizes = [high, medium, low]
            # Filter out zero values for cleaner chart
            labels_sizes = [(l, s) for l, s in zip(labels, sizes) if s > 0]
            if labels_sizes:
                clean_labels, clean_sizes = zip(*labels_sizes)
                colors_map = {'High Match (70-100%)': '#27ae60', 'Medium Match (40-69%)': '#f39c12', 'Low Match (<40%)': '#c0392b'}
                clean_colors = [colors_map[l] for l in clean_labels]
                
                fig = Figure(figsize=(8, 8))
                ax = fig.add_subplot(111)
                wedges, texts, autotexts = ax.pie(clean_sizes, labels=clean_labels, colors=clean_colors, autopct='%1.1f%%', startangle=140, pctdistance=0.85)
                
                # Draw circle for Donut Chart style
                centre_circle = plt.Circle((0,0),0.70,fc='white')
                # Add artist to axes
                ax.add_artist(centre_circle)
                
                ax.set_title('Match Quality Distribution (Taken Jobs)')
                plt.setp(autotexts, size=10, weight="bold", color="white")
                fig.tight_layout()
                context['chart_match_quality'] = self.get_plot_image(fig)
            else:
                context['chart_match_quality'] = None
        else:
            context['chart_match_quality'] = None

        # 4. Jobs Taken by Employees (Cumulative Line Chart - Last 6 Months)
        six_months_ago = timezone.now() - timedelta(days=180)
        jobs_filled = Job.objects.filter(filled_by__isnull=False, filled_at__gte=six_months_ago).values('filled_at')
        
        if jobs_filled:
            df_filled = pd.DataFrame(list(jobs_filled))
            df_filled['filled_at'] = pd.to_datetime(df_filled['filled_at'])
            df_filled['month'] = df_filled['filled_at'].dt.to_period('M')
            monthly_counts = df_filled.groupby('month').size().rename('count')
            start_period = pd.Timestamp(six_months_ago).to_period('M')
            end_period = pd.Timestamp(timezone.now()).to_period('M')
            month_range = pd.period_range(start=start_period, end=end_period, freq='M')
            full = pd.DataFrame({'month': month_range}).set_index('month').join(monthly_counts, how='left').fillna(0.0)
            full['count'] = full['count'].astype(int)
            full['cumulative'] = full['count'].cumsum()
            dates = full.index.to_timestamp()
            counts = full['cumulative'].values
            
            fig = Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            ax.plot(dates, counts, marker='o', linestyle='-', linewidth=2, color='#2980b9')
            ax.set_title('Jobs Taken Trend (Cumulative)')
            ax.set_ylabel('Cumulative Jobs')
            ax.set_xlabel('Month')
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Format X-axis dates
            import matplotlib.dates as mdates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            fig.autofmt_xdate()
            
            # Ensure integer Y-axis
            from matplotlib.ticker import MaxNLocator
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            
            context['chart_jobs_taken'] = self.get_plot_image(fig)
        else:
            context['chart_jobs_taken'] = None

        # Role specific context
        if user.role == 'employer':
            if hasattr(user, 'employer_profile'):
                context['my_jobs'] = Job.objects.filter(employer=user.employer_profile).order_by('-created_at')[:5]
        elif user.role == 'employee':
             pass
             
        return context
