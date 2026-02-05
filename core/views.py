from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from employees.models import EmployeeProfile
from employers.models import EmployerProfile
from jobs.models import Job
from core.models import Skill
from accounts.models import CustomUser

class HomeView(TemplateView):
    template_name = 'core/home.html'

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Common context
        context['total_employees'] = EmployeeProfile.objects.count()
        context['total_employers'] = EmployerProfile.objects.count()
        context['total_jobs'] = Job.objects.count()
        context['top_skills'] = Skill.objects.annotate(job_count=Count('job')).order_by('-job_count')[:5]
        
        # Role specific context
        if user.role == 'employer':
            if hasattr(user, 'employer_profile'):
                context['my_jobs'] = Job.objects.filter(employer=user.employer_profile).order_by('-created_at')[:5]
        elif user.role == 'employee':
             # For employees, maybe show recent matching jobs?
             pass
             
        return context
