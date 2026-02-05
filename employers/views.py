from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import EmployerProfile

class EmployerProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployerProfile
    fields = ['company_name', 'contact_email', 'phone', 'location']
    template_name = 'employers/profile_form.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self, queryset=None):
        return self.request.user.employer_profile

class EmployerCreateView(LoginRequiredMixin, CreateView):
    model = EmployerProfile
    fields = ['company_name', 'contact_email', 'phone', 'location']
    template_name = 'employers/profile_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class EmployerListView(LoginRequiredMixin, ListView):
    model = EmployerProfile
    template_name = 'employers/employer_list.html'
    context_object_name = 'employers'
