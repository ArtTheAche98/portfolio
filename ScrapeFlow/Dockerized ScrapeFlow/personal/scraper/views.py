from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings as django_settings
import requests
from jose import jwt
import datetime

from scraper.forms import (
    UserProfileForm, 
    SignUpForm, 
    LinkedInSettingsForm, 
    ScrapingScheduleForm
)
from scraper.models import ScrapingSchedule, ScrapedContent, UserProfile

def index(request):
    # Get real statistics
    total_scrapes = ScrapedContent.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    success_rate = 99.9  # This could be calculated from actual scraping success rates
    
    # Dynamic features list
    features = [
        {
            'icon': 'bi-code-square',
            'title': 'No-Code Automation',
            'description': 'Easily set up and manage scrapers with an intuitive interface—no coding needed.'
        },
        {
            'icon': 'bi-speedometer2',
            'title': 'Real-time Dashboard',
            'description': 'Monitor your scrapers and data in real-time from anywhere.'
        },
        {
            'icon': 'bi-cloud',
            'title': 'Cloud Storage',
            'description': 'Your data securely stored and accessible in the cloud.'
        },
        {
            'icon': 'bi-download',
            'title': 'Smart Scheduling',
            'description': 'Automate content publishing with a flexible, time-saving scheduling system.'
        }
    ]
    
    context = {
        'stats': {
            'total_scrapes': f"{total_scrapes:,}+",
            'active_users': f"{active_users:,}+",
            'success_rate': f"{success_rate}%"
        },
        'features': features
    }
    
    return render(request, 'scraper/index.html', context)

@login_required
def dashboard(request):
    user_schedules = ScrapingSchedule.objects.filter(user=request.user)
    recent_posts = ScrapedContent.objects.filter(
        schedule__user=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'schedule_form': ScrapingScheduleForm(),
        'schedules': user_schedules,
        'recent_posts': recent_posts,
    }
    return render(request, 'scraper/dashboard.html', context)

@login_required
def add_schedule(request):
    if request.method == 'POST':
        form = ScrapingScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
            schedule.next_run = timezone.now()
            schedule.save()
            messages.success(request, 'Schedule created successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('dashboard')

@login_required
def toggle_schedule(request, schedule_id):
    schedule = get_object_or_404(ScrapingSchedule, id=schedule_id, user=request.user)
    schedule.is_active = not schedule.is_active
    schedule.save()
    return redirect('dashboard')

@login_required
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(ScrapingSchedule, id=schedule_id, user=request.user)
    schedule.delete()
    messages.success(request, 'Schedule deleted successfully!')
    return redirect('dashboard')

@login_required
def linkedin_settings(request):
    if request.method == 'POST':
        form = LinkedInSettingsForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'LinkedIn settings updated successfully!')
            return redirect('dashboard')
    else:
        form = LinkedInSettingsForm(instance=request.user.userprofile)

    context = {
        'form': form,
        'settings': {
            'LINKEDIN_CLIENT_ID': django_settings.LINKEDIN_CLIENT_ID,
            'LINKEDIN_CLIENT_SECRET': bool(django_settings.LINKEDIN_CLIENT_SECRET),  # Just pass if it exists
            'LINKEDIN_REDIRECT_URI': django_settings.LINKEDIN_REDIRECT_URI,
        }
    }
    return render(request, 'scraper/linkedin_settings.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'scraper/login.html', {
        'form': form,
        'title': 'Login'
    })

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome aboard!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SignUpForm()
    return render(request, 'scraper/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'scraper/home.html', {'form': form})

@login_required
def linkedin_auth(request):
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={django_settings.LINKEDIN_CLIENT_ID}&redirect_uri={django_settings.LINKEDIN_REDIRECT_URI}&scope={'%20'.join(django_settings.LINKEDIN_SCOPE)}&state={request.user.id}"
    return redirect(auth_url)

@login_required
def linkedin_callback(request):
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'LinkedIn authentication failed.')
        return redirect('linkedin_settings')

    if not django_settings.LINKEDIN_CLIENT_ID or not django_settings.LINKEDIN_CLIENT_SECRET:
        messages.error(request, 'LinkedIn API credentials are not configured.')
        return redirect('linkedin_settings')

    try:
        # Exchange code for access token (and possibly an ID token)
        response = requests.post(
            'https://www.linkedin.com/oauth/v2/accessToken',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': django_settings.LINKEDIN_CLIENT_ID,
                'client_secret': django_settings.LINKEDIN_CLIENT_SECRET,
                'redirect_uri': django_settings.LINKEDIN_REDIRECT_URI,
            }
        )
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get('access_token')
        id_token = token_data.get('id_token')
        
        if id_token:
            # Decode the ID token to extract user info
            decoded = jwt.decode(id_token, options={"verify_signature": False})
            linkedin_user_id = decoded.get('sub')
            # Optionally get additional info
            # linkedin_email = decoded.get('email')
            # linkedin_name = decoded.get('name')
            
            # Save LinkedIn token and profile info using the decoded data
            request.user.userprofile.linkedin_token = access_token
            request.user.userprofile.linkedin_user_id = linkedin_user_id
            request.user.userprofile.save()
            
            messages.success(request, 'LinkedIn account connected successfully!')
        else:
            messages.error(request, 'ID token not provided in token response.')
    except requests.RequestException as e:
        messages.error(request, f'Failed to connect LinkedIn account: {str(e)}')
    
    return redirect('linkedin_settings')

@login_required
def remove_linkedin(request):
    if request.method == 'POST':
        request.user.userprofile.linkedin_token = ''
        request.user.userprofile.save()
        messages.success(request, 'LinkedIn account disconnected successfully.')
    return redirect('dashboard')
