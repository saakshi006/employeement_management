from django.db import models
from django.conf import settings
from core.models import Skill

class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    skills = models.ManyToManyField(Skill, blank=True)
    experience_years = models.IntegerField(default=0)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name
