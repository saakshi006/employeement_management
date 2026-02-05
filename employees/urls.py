from django.urls import path
from .views import EmployeeCreateView, EmployeeProfileUpdateView, EmployeeListView, MatchingJobsView

urlpatterns = [
    path('create-profile/', EmployeeCreateView.as_view(), name='create_employee_profile'),
    path('update-profile/', EmployeeProfileUpdateView.as_view(), name='update_employee_profile'),
    path('list/', EmployeeListView.as_view(), name='employee_list'),
    path('matching/', MatchingJobsView.as_view(), name='matching_jobs'),
]
