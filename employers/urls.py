from django.urls import path
from .views import EmployerCreateView, EmployerProfileUpdateView, EmployerListView

urlpatterns = [
    path('create-profile/', EmployerCreateView.as_view(), name='create_employer_profile'),
    path('update-profile/', EmployerProfileUpdateView.as_view(), name='update_employer_profile'),
    path('list/', EmployerListView.as_view(), name='employer_list'),
]
