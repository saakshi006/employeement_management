from django.db import models
from employers.models import EmployerProfile
from core.models import Skill

class Job(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=100)
    required_skills = models.ManyToManyField(Skill, blank=True)
    experience_required = models.IntegerField(default=0)
    salary = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    filled_by = models.ForeignKey('employees.EmployeeProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs_taken')
    filled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
