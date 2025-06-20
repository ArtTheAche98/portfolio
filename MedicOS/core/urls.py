from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('patient/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patient/<int:patient_id>/add-medication/', views.add_medication, name='add_medication'),
]