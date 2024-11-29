from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update-request/<int:request_id>/', views.update_request_status, name='update_request_status'),
]
