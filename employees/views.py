from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import EmployeeProfile
from jobs.models import Job

class EmployeeProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployeeProfile
    fields = ['name', 'age', 'skills', 'experience_years', 'phone', 'location']
    template_name = 'employees/profile_form.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user.employee_profile

class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = EmployeeProfile
    fields = ['name', 'age', 'skills', 'experience_years', 'phone', 'location']
    template_name = 'employees/profile_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EmployeeListView(LoginRequiredMixin, ListView):
    model = EmployeeProfile
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    
    def get_queryset(self):
        # Implement search here
        queryset = super().get_queryset()
        skill_query = self.request.GET.get('skill')
        location_query = self.request.GET.get('location')
        
        if skill_query:
            queryset = queryset.filter(skills__name__icontains=skill_query)
        if location_query:
            queryset = queryset.filter(location__icontains=location_query)
            
        return queryset.distinct()

class MatchingJobsView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'employees/matching_jobs.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'employee_profile'):
            return Job.objects.none()
        
        employee = user.employee_profile
        employee_skills = set(employee.skills.all())
        
        jobs = Job.objects.all()
        matched_jobs = []
        
        for job in jobs:
            job_skills = set(job.required_skills.all())
            if not job_skills:
                skill_match = 100
            else:
                matching_skills = employee_skills.intersection(job_skills)
                skill_match = (len(matching_skills) / len(job_skills)) * 100
            
            # Experience Match
            if employee.experience_years >= job.experience_required:
                exp_match = 100
            else:
                if job.experience_required > 0:
                    exp_match = (employee.experience_years / job.experience_required) * 100
                else:
                    exp_match = 100
            
            total_score = (skill_match * 0.7) + (exp_match * 0.3)
            
            job.match_score = round(total_score, 1)
            job.skill_gap = job_skills - employee_skills
            job.skill_match_percent = round(skill_match, 1)
            job.exp_match_percent = round(exp_match, 1)
            
            matched_jobs.append(job)
            
        return sorted(matched_jobs, key=lambda x: x.match_score, reverse=True)
