from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Job

class JobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        skill_query = self.request.GET.get('skill')
        location_query = self.request.GET.get('location')
        
        if skill_query:
            queryset = queryset.filter(required_skills__name__icontains=skill_query)
        if location_query:
            queryset = queryset.filter(location__icontains=location_query)
            
        return queryset.distinct()

class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    fields = ['title', 'required_skills', 'experience_required', 'salary', 'location']
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.employer = self.request.user.employer_profile
        return super().form_valid(form)

class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Job
    fields = ['title', 'required_skills', 'experience_required', 'salary', 'location']
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        job = self.get_object()
        return self.request.user.employer_profile == job.employer

class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Job
    template_name = 'jobs/job_confirm_delete.html'
    success_url = reverse_lazy('dashboard')

    def test_func(self):
        job = self.get_object()
        return self.request.user.employer_profile == job.employer
