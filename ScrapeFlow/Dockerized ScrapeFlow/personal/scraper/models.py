from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.CharField(max_length=100, blank=True)
    linkedin_token = models.TextField(blank=True, help_text="OAuth token for LinkedIn")
    linkedin_user_id = models.CharField(max_length=100, blank=True, help_text="LinkedIn User ID for posting")
    monthly_scrape_limit = models.IntegerField(default=100)
    scrapes_this_month = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Scraper(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.URLField()
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('ONCE', 'One-time'),
            ('DAILY', 'Daily'),
            ('WEEKLY', 'Weekly'),
            ('MONTHLY', 'Monthly')
        ],
        default='ONCE'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', 'Active'),
            ('PAUSED', 'Paused'),
            ('FAILED', 'Failed'),
            ('COMPLETED', 'Completed')
        ],
        default='ACTIVE'
    )
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ScrapingSchedule(models.Model):
    INTERVAL_CHOICES = [
        ('6H', 'Every 6 Hours'),
        ('12H', 'Every 12 Hours'),
        ('24H', 'Daily'),
        ('48H', 'Every 2 Days'),
        ('72H', 'Every 3 Days'),
        ('168H', 'Weekly'),
    ]

    POST_STYLE_CHOICES = [
        ('NEWS', 'News Style'),
        ('INSIGHTS', 'Industry Insights'),
        ('SUMMARY', 'Brief Summary'),
        ('QUOTES', 'Key Quotes'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source_url = models.URLField(help_text="URL of the blog/website to scrape")
    topic = models.CharField(max_length=200, help_text="Topic or category to focus on")
    custom_title = models.CharField(max_length=300, blank=True, help_text="Custom title template for posts")
    interval = models.CharField(max_length=4, choices=INTERVAL_CHOICES, default='24H')
    post_style = models.CharField(max_length=10, choices=POST_STYLE_CHOICES, default='NEWS')
    hashtags = models.CharField(max_length=500, blank=True, help_text="Comma-separated hashtags for LinkedIn posts")
    custom_template = models.TextField(blank=True, help_text="Custom post template. Use {title}, {summary}, {url} as placeholders")
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.next_run:
            self.next_run = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s schedule for {self.source_url}"

class ScrapedContent(models.Model):
    schedule = models.ForeignKey(ScrapingSchedule, on_delete=models.CASCADE)
    original_url = models.URLField()
    title = models.CharField(max_length=300)
    content = models.TextField()
    summary = models.TextField()
    linkedin_post_text = models.TextField()
    posted_to_linkedin = models.BooleanField(default=False)
    linkedin_post_id = models.CharField(max_length=100, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Content: {self.title[:50]}..."

    class Meta:
        ordering = ['-created_at']

class ScrapedData(models.Model):
    scraper = models.ForeignKey(Scraper, on_delete=models.CASCADE)
    data = models.JSONField()
    scraped_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-scraped_at']

    def __str__(self):
        return f"Data for {self.scraper.name} at {self.scraped_at}"

# Signal to create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()