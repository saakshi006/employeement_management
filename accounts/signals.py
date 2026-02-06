from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser
from employees.models import EmployeeProfile
from employers.models import EmployerProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == CustomUser.EMPLOYEE:
            EmployeeProfile.objects.create(
                user=instance,
                name=instance.username,  # Default name
                age=0,                  # Default
                experience_years=0,     # Default
                phone='',               # Default
                location=''             # Default
            )
        elif instance.role == CustomUser.EMPLOYER:
            EmployerProfile.objects.create(
                user=instance,
                company_name=instance.username, # Default
                contact_email=instance.email,
                phone='',
                location=''
            )

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == CustomUser.EMPLOYEE:
        if hasattr(instance, 'employee_profile'):
            instance.employee_profile.save()
    elif instance.role == CustomUser.EMPLOYER:
        if hasattr(instance, 'employer_profile'):
            instance.employer_profile.save()
