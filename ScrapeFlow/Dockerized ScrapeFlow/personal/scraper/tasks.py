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
    ).select_related('user__userprofile')  # Optimize query
    
    session = HTMLSession()
    for schedule in due_schedules:
        try:
            # Fetch the page
            response = session.get(schedule.source_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find main content (this might need adjustment based on the target site)
            article = soup.find('article') or soup.find('main') or soup.find('div', class_=['post', 'article', 'content'])
            title = soup.find('h1')
            
            if not article:
                logger.warning(f"Could not find main content for {schedule.source_url}")
                content = soup.get_text(separator="\n", strip=True)  # Fallback to full page content
            else:
                content = article.get_text(separator="\n", strip=True)
            
            # Extract title from content if not found
            if (title):
                title = title.text.strip()
            else:
                title = f"Update from {schedule.source_url}"
            
            # Use the optimizer to create a refined LinkedIn post text
            post_style = getattr(schedule, 'post_style', 'INSIGHTS')
            optimized_post = content_optimizer.optimize_content(
                f"Title: {title}\n\nContent: {content[:1000]}...",
                style=post_style
            )
            
            if not optimized_post:
                optimized_post = f"""🔥 New {schedule.topic} Update 🔥

{title}

Key Insights:
{content[:200]}...

Read more: {schedule.source_url}

#{schedule.topic.replace(' ', '')} #Innovation #Technology"""
            
            # Create a new ScrapedContent post
            scraped_content = ScrapedContent.objects.create(
                schedule=schedule,
                original_url=schedule.source_url,
                title=title,
                content=content,
                summary=content[:500],
                linkedin_post_text=optimized_post
            )
            
            # Immediately trigger LinkedIn posting if credentials exist
            if schedule.user.userprofile.linkedin_token and schedule.user.userprofile.linkedin_user_id:
                post_to_linkedin.delay(scraped_content.id)
                logger.info(f"Triggered LinkedIn posting for content {scraped_content.id}")
            else:
                logger.warning(f"LinkedIn credentials missing for schedule {schedule.id}")
            
            logger.info(f"Created post for schedule {schedule.id}")
        except Exception as e:
            logger.error(f"Error processing schedule {schedule.id}: {str(e)}")
        
        # Update schedule timings
        schedule.last_run = now
        interval_map = {
            '6H': timedelta(hours=6),
            '12H': timedelta(hours=12),
            '24H': timedelta(hours=24),
            '48H': timedelta(hours=48),
            '72H': timedelta(hours=72),
            '168H': timedelta(hours=168)
        }
        schedule.next_run = now + interval_map.get(schedule.interval, timedelta(hours=24))
        schedule.save(update_fields=['last_run', 'next_run'])
    
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

@shared_task(bind=True, max_retries=3)
def post_to_linkedin(self, content_id):
    """Post the content to LinkedIn"""
    logger.info(f"Starting post_to_linkedin task for content ID: {content_id}")
    try:
        content = ScrapedContent.objects.select_related('schedule__user__userprofile').get(id=content_id)
        profile = content.schedule.user.userprofile
        
        if not profile.linkedin_token or not profile.linkedin_user_id:
            logger.error(f"LinkedIn credentials missing for content {content_id}")
            return
        
        headers = {
            'Authorization': f'Bearer {profile.linkedin_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'  # Required for LinkedIn's API
        }
        
        # LinkedIn API endpoint for creating posts
        url = 'https://api.linkedin.com/v2/ugcPosts'
        
        # Prepare the post data with hashtags if available
        post_text = content.linkedin_post_text
        if content.schedule.hashtags:
            hashtags = ' '.join(f"#{tag.strip()}" for tag in content.schedule.hashtags.split(','))
            post_text = f"{post_text}\n\n{hashtags}"
        
        post_data = {
            "author": f"urn:li:person:{profile.linkedin_user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(url, headers=headers, json=post_data)
        response.raise_for_status()
        
        # Update the content with LinkedIn post ID and status
        content.linkedin_post_id = response.json().get('id')
        content.posted_to_linkedin = True
        content.posted_at = timezone.now()
        content.save(update_fields=['linkedin_post_id', 'posted_to_linkedin', 'posted_at'])
        
        logger.info(f"Successfully posted content ID: {content_id} to LinkedIn")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"LinkedIn API error for content {content_id}: {str(e)}")
        # Retry the task with exponential backoff
        retry_in = (2 ** self.request.retries) * 60  # 1min, 2min, 4min
        raise self.retry(exc=e, countdown=retry_in)
    except Exception as e:
        logger.error(f"Unexpected error posting content {content_id}: {str(e)}")
        if not self.request.retries:
            # Only retry on first attempt for unexpected errors
            raise self.retry(exc=e, countdown=60)

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