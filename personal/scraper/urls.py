from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('schedule/add/', views.add_schedule, name='add_schedule'),
    path('schedule/toggle/<int:schedule_id>/', views.toggle_schedule, name='toggle_schedule'),
    path('schedule/delete/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('linkedin/settings/', views.linkedin_settings, name='linkedin_settings'),
    path('linkedin/auth/', views.linkedin_auth, name='linkedin_auth'),
    path('linkedin/callback/', views.linkedin_callback, name='linkedin_callback'),
    path('linkedin/remove/', views.remove_linkedin, name='remove_linkedin'),
]