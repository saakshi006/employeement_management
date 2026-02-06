from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Skill
from employees.models import EmployeeProfile
from employers.models import EmployerProfile
from jobs.models import Job
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Loads sample data for the Skill Match System'

    def handle(self, *args, **kwargs):
        self.stdout.write('Deleting old data...')
        Job.objects.all().delete()
        EmployeeProfile.objects.all().delete()
        EmployerProfile.objects.all().delete()
        # User.objects.exclude(is_superuser=True).delete()
        for user in User.objects.all():
            if not user.is_superuser:
                user.delete()
        Skill.objects.all().delete()

        self.stdout.write('Creating skills...')
        skills_list = [
            'Plumbing', 'Tailoring', 'Cooking', 'Cleaning', 'Driving', 
            'Electrician', 'Carpentry', 'Masonry', 'Security Guard', 
            'Housekeeping', 'Painting', 'Babysitting', 'Laundry', 'Gardening',
            'Communication', 'Teamwork', 'Labor'
        ]
        skills_objs = []
        for name in skills_list:
            skill, _ = Skill.objects.get_or_create(name=name)
            skills_objs.append(skill)

        self.stdout.write('Creating users and profiles...')
        
        # 1. Admin
        # if not User.objects.filter(username='admin').exists():
        if User.objects.filter(username='admin').count() == 0:
            User.objects.create_superuser('admin', 'admin@system.com', 'admin123', role='admin')
        else:
            # Ensure admin has correct password if it exists (for demo purposes)
            try:
                u = User.objects.get(username='admin')
                u.set_password('admin123')
                u.save()
            except:
                pass

        # 2. Demo Employer (Specific Account)
        demo_employer = User.objects.create_user(username='employer', email='employer@demo.com', password='employer123', role='employer')
        EmployerProfile.objects.create(
            user=demo_employer,
            company_name='Local Services Agency',
            contact_email='employer@demo.com',
            phone='9876543210',
            location='Mumbai'
        )

        # 3. Demo Employee (Specific Account)
        demo_employee = User.objects.create_user(username='employee', email='employee@employee.com', password='employee123', role='employee')
        emp_profile = EmployeeProfile.objects.create(
            user=demo_employee,
            name='Raju Plumber',
            age=28,
            experience_years=5,
            phone='9123456780',
            location='Mumbai'
        )
        emp_profile.skills.add(Skill.objects.get(name='Plumbing'), Skill.objects.get(name='Electrician'))

        # 4. Additional Employers
        employer_data = [
            ('City Construction Co', 'construction@demo.com', 'Mumbai'),
            ('Home Helpers Agency', 'helpers@demo.com', 'Delhi'),
            ('Tasty Tiffin Service', 'tiffin@demo.com', 'Bangalore'),
            ('Secure Guards Ltd', 'security@demo.com', 'Pune'),
            ('Daily Needs Manpower', 'daily@demo.com', 'Chennai'),
        ]
        
        employers = [demo_employer.employer_profile] # Start with demo employer
        for i, (company, email, loc) in enumerate(employer_data):
            username = f'employer{i+1}'
            user = User.objects.create_user(username=username, email=email, password='employer123', role='employer')
            profile = EmployerProfile.objects.create(
                user=user,
                company_name=company,
                contact_email=email,
                phone=f'987654321{i+1}',
                location=loc
            )
            employers.append(profile)

        # 5. Additional Employees
        employee_data = [
            ('Sunita Devi', 35, 10, 'Mumbai', ['Tailoring', 'Cooking']),
            ('Ramesh Kumar', 22, 2, 'Delhi', ['Driving', 'Labor']),
            ('Lakshmi Patel', 40, 15, 'Pune', ['Cooking', 'Cleaning', 'Housekeeping']),
            ('Abdul Khan', 28, 5, 'Bangalore', ['Carpentry', 'Painting']),
            ('Vijay Singh', 24, 1, 'Mumbai', ['Security Guard', 'Labor']),
            ('Deepak Verma', 30, 8, 'Delhi', ['Electrician', 'Plumbing']),
            ('Anita Gupta', 26, 4, 'Chennai', ['Babysitting', 'Laundry']),
            ('Sanjay Yadav', 29, 6, 'Pune', ['Gardening', 'Labor']),
        ]

        for i, (name, age, exp, loc, skill_names) in enumerate(employee_data):
            username = f'employee{i+1}'
            user = User.objects.create_user(username=username, email=f'emp{i+1}@employee.com', password='employee123', role='employee')
            profile = EmployeeProfile.objects.create(
                user=user,
                name=name,
                age=age,
                experience_years=exp,
                phone=f'912345678{i+1}',
                location=loc
            )
            for s_name in skill_names:
                skill = Skill.objects.get(name=s_name)
                profile.skills.add(skill)

        self.stdout.write('Creating jobs...')
        # Jobs (Expanded list for better charts)
        job_data = [
            (0, 'Experienced Plumber Needed', ['Plumbing'], 5, '15000', 'Mumbai'),
            (1, 'Construction Laborer', ['Labor', 'Masonry'], 1, '12000', 'Mumbai'),
            (2, 'House Maid Wanted', ['Cleaning', 'Cooking'], 2, '10000', 'Delhi'),
            (3, 'Cook for Tiffin Service', ['Cooking'], 3, '14000', 'Bangalore'),
            (4, 'Night Security Guard', ['Security Guard'], 1, '13000', 'Pune'),
            (4, 'Security Supervisor', ['Security Guard', 'Teamwork'], 8, '20000', 'Pune'),
            (5, 'Driver for Family', ['Driving'], 4, '16000', 'Chennai'),
            (0, 'Electrician for Shop', ['Electrician'], 3, '18000', 'Mumbai'),
            (1, 'Site Manager', ['Teamwork', 'Communication'], 5, '25000', 'Mumbai'),
            (2, 'Nanny', ['Babysitting'], 2, '11000', 'Delhi'),
            (3, 'Kitchen Helper', ['Cleaning'], 0, '9000', 'Bangalore'),
            (5, 'Valet Driver', ['Driving'], 2, '15000', 'Chennai'),
            (0, 'Home Painter', ['Painting'], 3, '14000', 'Mumbai'),
            (4, 'Bodyguard', ['Security Guard'], 5, '22000', 'Pune'),
            (2, 'Gardener', ['Gardening'], 1, '8000', 'Delhi'),
        ]

        all_employees = list(EmployeeProfile.objects.all())

        for i, (emp_idx, title, req_skills, exp, sal, loc) in enumerate(job_data):
            # emp_idx maps to employers list which includes demo employer at index 0
            if emp_idx < len(employers):
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
                
                # Intentionally create distributed matches (High, Medium, Low)
                # We'll fill about 70% of the jobs
                if i % 10 < 7 and all_employees: 
                    # Deterministic assignment to ensure distribution
                    # Modulo 3: 0 -> High match, 1 -> Medium match, 2 -> Low match
                    
                    match_type = i % 3
                    selected_emp = None
                    
                    job_skills = set(job.required_skills.all())
                    
                    if match_type == 0: # Try to find High Match (All skills + good exp)
                        candidates = [e for e in all_employees if set(e.skills.all()).issuperset(job_skills) and e.experience_years >= exp]
                        if candidates: selected_emp = random.choice(candidates)
                    
                    elif match_type == 1: # Try to find Medium Match (Some skills or exp mismatch)
                        candidates = [e for e in all_employees if set(e.skills.all()).intersection(job_skills) and not set(e.skills.all()).issuperset(job_skills)]
                        if candidates: selected_emp = random.choice(candidates)
                        
                    elif match_type == 2: # Try to find Low Match (No skills overlap)
                        candidates = [e for e in all_employees if not set(e.skills.all()).intersection(job_skills)]
                        if candidates: selected_emp = random.choice(candidates)
                    
                    # Fallback if specific match type not found
                    if not selected_emp:
                        selected_emp = random.choice(all_employees)

                    job.filled_by = selected_emp
                    # Spread dates over last 6 months for better line chart
                    days_ago = random.randint(0, 180)
                    job.filled_at = timezone.now() - timedelta(days=days_ago)
                    job.save()

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data'))
