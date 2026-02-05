from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Skill
from employees.models import EmployeeProfile
from employers.models import EmployerProfile
from jobs.models import Job
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Loads sample data for the Skill Match System'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        Job.objects.all().delete()
        EmployeeProfile.objects.all().delete()
        EmployerProfile.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        Skill.objects.all().delete()

        self.stdout.write('Creating skills...')
        skills_list = [
            'Python', 'Django', 'JavaScript', 'HTML', 'CSS', 'React', 'SQL', 
            'Communication', 'Teamwork', 'Leadership', 'Data Analysis', 'Sales',
            'Driving', 'Cooking', 'Cleaning', 'Carpentry', 'Plumbing'
        ]
        skills_objs = []
        for name in skills_list:
            skill, _ = Skill.objects.get_or_create(name=name)
            skills_objs.append(skill)

        self.stdout.write('Creating users and profiles...')
        
        # Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@system.com', 'admin123', role='admin')
        
        # Employers (5)
        employer_data = [
            ('Tech Solutions', 'tech@demo.com', 'Mumbai'),
            ('City Services', 'city@demo.com', 'Delhi'),
            ('Food Express', 'food@demo.com', 'Bangalore'),
            ('BuildIt Construction', 'build@demo.com', 'Pune'),
            ('Home Helpers', 'home@demo.com', 'Chennai'),
        ]
        
        employers = []
        for i, (company, email, loc) in enumerate(employer_data):
            username = f'employer{i+1}'
            user = User.objects.create_user(username=username, email=email, password='employer123', role='employer')
            profile = EmployerProfile.objects.create(
                user=user,
                company_name=company,
                contact_email=email,
                phone=f'987654321{i}',
                location=loc
            )
            employers.append(profile)

        # Employees (8)
        employee_data = [
            ('Ravi Kumar', 25, 3, 'Mumbai', ['Python', 'Django', 'SQL']),
            ('Anita Singh', 22, 1, 'Delhi', ['HTML', 'CSS', 'JavaScript']),
            ('Suresh Patel', 30, 8, 'Pune', ['Driving', 'Communication']),
            ('Meena Devi', 28, 5, 'Bangalore', ['Cooking', 'Cleaning']),
            ('Rahul Sharma', 24, 2, 'Mumbai', ['Sales', 'Communication']),
            ('Vikram Singh', 35, 10, 'Delhi', ['Carpentry', 'Plumbing']),
            ('Priya Gupta', 26, 4, 'Chennai', ['Data Analysis', 'Python']),
            ('Amit Verma', 29, 6, 'Pune', ['Leadership', 'Teamwork', 'Sales']),
        ]

        for i, (name, age, exp, loc, skill_names) in enumerate(employee_data):
            username = f'employee{i+1}'
            user = User.objects.create_user(username=username, email=f'emp{i+1}@employee.com', password='employee123', role='employee')
            profile = EmployeeProfile.objects.create(
                user=user,
                name=name,
                age=age,
                experience_years=exp,
                phone=f'912345678{i}',
                location=loc
            )
            for s_name in skill_names:
                skill = Skill.objects.get(name=s_name)
                profile.skills.add(skill)

        self.stdout.write('Creating jobs...')
        # Jobs (7)
        job_data = [
            (0, 'Python Developer', ['Python', 'Django'], 2, '50000', 'Mumbai'),
            (0, 'Backend Engineer', ['Python', 'SQL'], 4, '80000', 'Mumbai'),
            (1, 'Frontend Intern', ['HTML', 'CSS'], 0, '15000', 'Delhi'),
            (2, 'Chef', ['Cooking'], 3, '30000', 'Bangalore'),
            (3, 'Site Supervisor', ['Leadership', 'Teamwork'], 5, '45000', 'Pune'),
            (3, 'Laborer', ['Teamwork'], 0, '12000', 'Pune'),
            (4, 'Housekeeper', ['Cleaning', 'Cooking'], 1, '18000', 'Chennai'),
        ]

        for emp_idx, title, req_skills, exp, sal, loc in job_data:
            job = Job.objects.create(
                employer=employers[emp_idx],
                title=title,
                experience_required=exp,
                salary=sal,
                location=loc
            )
            for s_name in req_skills:
                skill = Skill.objects.get(name=s_name)
                job.required_skills.add(skill)

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data'))
