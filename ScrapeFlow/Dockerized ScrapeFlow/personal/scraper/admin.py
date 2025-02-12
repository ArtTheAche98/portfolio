from django.contrib import admin
from .models import UserProfile, Scraper, ScrapingSchedule, ScrapedContent, ScrapedData

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'monthly_scrape_limit', 'scrapes_this_month', 'created_at')
    search_fields = ('user__username', 'user__email')

@admin.register(Scraper)
class ScraperAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'frequency', 'status', 'last_run', 'next_run')
    list_filter = ('status', 'frequency')
    search_fields = ('name', 'user__username')

@admin.register(ScrapingSchedule)
class ScrapingScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'source_url', 'topic', 'interval', 'is_active', 'next_run')
    list_filter = ('is_active', 'interval', 'post_style')
    search_fields = ('topic', 'user__username', 'source_url')

@admin.register(ScrapedContent)
class ScrapedContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'schedule', 'posted_to_linkedin', 'posted_at', 'created_at')
    list_filter = ('posted_to_linkedin',)
    search_fields = ('title', 'content', 'schedule__topic')

@admin.register(ScrapedData)
class ScrapedDataAdmin(admin.ModelAdmin):
    list_display = ('scraper', 'scraped_at', 'success')
    list_filter = ('success',)
    search_fields = ('scraper__name',)
