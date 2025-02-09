import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import requests
from django.conf import settings
from .models import ScrapingSchedule, ScrapedContent
from .services import ContentOptimizer
import datetime

logger = logging.getLogger(__name__)
content_optimizer = ContentOptimizer()

@shared_task
def process_scraping_schedules():
    """Check and process all active scraping schedules"""
    logger.info("Starting process_scraping_schedules task")
    now = timezone.now()
    due_schedules = ScrapingSchedule.objects.filter(
        is_active=True,
        next_run__lte=now
    )
    
    session = HTMLSession()
    for schedule in due_schedules:
        try:
            # Fetch the page
            response = session.get(schedule.source_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract main content; adjust selector as needed
            content = soup.get_text(separator="\n", strip=True)
            
            # Use the optimizer to create a refined LinkedIn post text.
            # The style can be stored on the schedule or be set to a default value.
            post_style = getattr(schedule, 'post_style', 'INSIGHTS')
            optimized_post = content_optimizer.optimize_content(content, style=post_style)
            
            # Create a new ScrapedContent post
            ScrapedContent.objects.create(
                schedule=schedule,
                original_url=schedule.source_url,
                title=schedule.custom_title or f"Scraped Post from {schedule.source_url}",
                content=content,
                summary=optimized_post[:150],
                linkedin_post_text=optimized_post
            )
            
            logger.info(f"Created post for schedule {schedule.id}")
        except Exception as e:
            logger.error(f"Error processing schedule {schedule.id}: {str(e)}")
        
        # Update schedule timings based on its interval setting
        schedule.last_run = now
        if schedule.interval == '6H':
            schedule.next_run = now + timedelta(hours=6)
        elif schedule.interval == '12H':
            schedule.next_run = now + timedelta(hours=12)
        elif schedule.interval == '24H':
            schedule.next_run = now + timedelta(hours=24)
        elif schedule.interval == '48H':
            schedule.next_run = now + timedelta(hours=48)
        elif schedule.interval == '72H':
            schedule.next_run = now + timedelta(hours=72)
        elif schedule.interval == '168H':
            schedule.next_run = now + timedelta(hours=168)
        else:
            # Default to 24 hours if not set
            schedule.next_run = now + timedelta(hours=24)
        schedule.save()
    
    logger.info("Completed process_scraping_schedules task")

@shared_task
def scrape_and_post(schedule_id):
    """Scrape content and post to LinkedIn"""
    logger.info(f"Starting scrape_and_post task for schedule ID: {schedule_id}")
    schedule = ScrapingSchedule.objects.get(id=schedule_id)
    
    try:
        # Create an HTML session
        session = HTMLSession()
        r = session.get(schedule.source_url)
        r.html.render(timeout=20)  # This will execute JavaScript

        # Parse the content
        soup = BeautifulSoup(r.html.html, 'lxml')
        
        # Find main content (this might need adjustment based on the target site)
        article = soup.find('article') or soup.find('main') or soup.find('div', class_['post', 'article', 'content'])
        
        if not article:
            raise Exception("Could not find main content")

        title = soup.find('h1').text.strip()
        content = article.get_text(strip=True)

        logger.info(f"Scraped content: {content[:200]}...")

        # Use DeepSeek to optimize the content
        optimized_content = content_optimizer.optimize_content(
            f"Title: {title}\n\nContent: {content[:1000]}...",  # Send first 1000 chars for optimization
            style=schedule.post_style
        )

        if not optimized_content:
            optimized_content = f"""🔥 New {schedule.topic} Update 🔥

{title}

Key Insights:
{content[:200]}...

Read more: {schedule.source_url}

##{schedule.topic.replace(' ', '')} #Innovation #Technology"""

        logger.info(f"Optimized content: {optimized_content[:200]}...")

        # Save the scraped content
        scraped_content = ScrapedContent.objects.create(
            schedule=schedule,
            original_url=schedule.source_url,
            title=title,
            content=content,
            summary=content[:500],
            linkedin_post_text=optimized_content
        )

        logger.info(f"Saved scraped content with ID: {scraped_content.id}")

        # Post to LinkedIn if token exists
        if schedule.user.userprofile.linkedin_token:
            logger.info(f"Scheduling post_to_linkedin task for content ID: {scraped_content.id}")
            post_to_linkedin.delay(scraped_content.id)

    except Exception as e:
        logger.error(f"Error processing {schedule.source_url}: {str(e)}")

@shared_task
def post_to_linkedin(content_id):
    """Post the content to LinkedIn"""
    logger.info(f"Starting post_to_linkedin task for content ID: {content_id}")
    content = ScrapedContent.objects.get(id=content_id)
    profile = content.schedule.user.userprofile
    
    if not profile.linkedin_token:
        logger.warning("LinkedIn token not found. Skipping post.")
        return
    
    headers = {
        'Authorization': f'Bearer {profile.linkedin_token}',
        'Content-Type': 'application/json',
    }
    
    # LinkedIn API endpoint for creating posts
    url = 'https://api.linkedin.com/v2/ugcPosts'
    
    # Prepare the post data
    post_data = {
        "author": f"urn:li:person:{profile.linkedin_user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": content.linkedin_post_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=post_data)
        response.raise_for_status()
        
        # Update the content with LinkedIn post ID
        content.linkedin_post_id = response.json().get('id')
        content.posted_to_linkedin = True
        content.posted_at = timezone.now()
        content.save()
        logger.info(f"Successfully posted content ID: {content_id} to LinkedIn")
        
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {str(e)}")

@shared_task
def process_schedules():
    now = timezone.now()
    schedules = ScrapingSchedule.objects.filter(is_active=True, next_run__lte=now)
    for schedule in schedules:
        # Replace this with your actual scraping logic.
        post_title = f"Sample post from {schedule.source_url}"
        post_content = "This is test content generated by the scraping task."
        # Create a new ScrapedContent (post)
        ScrapedContent.objects.create(
            schedule=schedule,
            original_url=schedule.source_url,
            title=post_title,
            content=post_content,
            summary=post_content[:150],
            linkedin_post_text=post_content
        )
        # Update schedule timings
        schedule.last_run = now
        if schedule.interval == '6H':
            schedule.next_run = now + datetime.timedelta(hours=6)
        elif schedule.interval == '12H':
            schedule.next_run = now + datetime.timedelta(hours=12)
        elif schedule.interval == '24H':
            schedule.next_run = now + datetime.timedelta(hours=24)
        elif schedule.interval == '48H':
            schedule.next_run = now + datetime.timedelta(hours=48)
        elif schedule.interval == '72H':
            schedule.next_run = now + datetime.timedelta(hours=72)
        elif schedule.interval == '168H':
            schedule.next_run = now + datetime.timedelta(hours=168)
        schedule.save()

@shared_task
def debug_task():
    logger.info("Debug task executed at: {}".format(timezone.now()))
    print("Debug task executed at: {}".format(timezone.now()))