from django.urls import path
from .views import JobListView, JobCreateView, JobUpdateView, JobDeleteView, JobApplyView

urlpatterns = [
    path('list/', JobListView.as_view(), name='job_list'),
    path('create/', JobCreateView.as_view(), name='create_job'),
    path('update/<int:pk>/', JobUpdateView.as_view(), name='update_job'),
    path('delete/<int:pk>/', JobDeleteView.as_view(), name='delete_job'),
    path('apply/<int:pk>/', JobApplyView.as_view(), name='apply_job'),
]
