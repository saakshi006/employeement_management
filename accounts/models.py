from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ADMIN = 'admin'
    EMPLOYER = 'employer'
    EMPLOYEE = 'employee'
    
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (EMPLOYER, 'Employer'),
        (EMPLOYEE, 'Employee'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=EMPLOYEE)
    
    def is_employer(self):
        return self.role == self.EMPLOYER
        
    def is_employee(self):
        return self.role == self.EMPLOYEE
        
    def is_admin_role(self):
        return self.role == self.ADMIN or self.is_superuser
