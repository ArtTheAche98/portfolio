from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ScrapingSchedule, UserProfile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm your password'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class LinkedInSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('linkedin_token',)
        widgets = {
            'linkedin_token': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ScrapingScheduleForm(forms.ModelForm):
    class Meta:
        model = ScrapingSchedule
        fields = ('source_url', 'topic', 'interval', 'post_style', 'hashtags', 'custom_template')
        widgets = {
            'source_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://blog.example.com'}),
            'topic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'AI, Technology, Business, etc.'}),
            'interval': forms.Select(attrs={'class': 'form-control'}),
            'post_style': forms.Select(attrs={'class': 'form-control'}),
            'hashtags': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'tech, innovation, ai (without #)'
            }),
            'custom_template': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': '🔥 {title}\n\nKey Insights:\n{summary}\n\nRead more: {url}\n\n#tech #innovation'
            }),
        }