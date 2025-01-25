import time
import logging
import random
import os
import requests
import schedule
from crawl4ai import WebCrawler
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import signal
import sys
import pickle

# Load environment variables
load_dotenv()
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")
TWITTER_MAIL = os.getenv("TWITTER_MAIL")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Constants
NEWS_SOURCES = [
    "https://deepmind.com/blog",
    "https://www.wired.com/category/artificial-intelligence/",
    "https://www.zdnet.com/topic/artificial-intelligence/",
    "https://allenai.org/blog",
    "https://blog.tensorflow.org/",
    "https://paperswithcode.com/",
    "https://www.deeplearning.ai/the-batch/",
    "https://ai.googleblog.com",
    "https://techcrunch.com/category/artificial-intelligence/",
    "https://ai.facebook.com/blog/",
    "https://www.theverge.com/ai-artificial-intelligence",
    "https://syncedreview.com/",
    "https://venturebeat.com/category/ai/",
]
POSTED_ARTICLES = set()
MAX_TWEET_LENGTH = 280
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("news_bot.log"), logging.StreamHandler()],
)


def main():
    driver = initialize_driver()
    posted_articles = load_posted_articles()

    try:
        # Load cookies if available
        driver.get("https://twitter.com")
        load_cookies(driver)

        if not is_logged_in(driver):
            logging.info("Not logged in. Attempting to log in...")
            if not login_to_twitter(driver):
                logging.error("Login failed. Exiting...")
                return  # Exit if login fails

            # Handle post-login verification (if necessary)
            handle_post_login(driver)

            # Verify login after attempting to log in
            if not is_logged_in(driver):
                logging.error("Unable to verify login. Exiting...")
                return

        # Schedule the job to run every 2 hours
        job(driver=driver, posted_articles=posted_articles)
        logging.info("Scheduling the job to run every 2 hours...")
        schedule.every(2).hours.do(job, driver=driver, posted_articles=posted_articles)

        # Schedule scrolling every 5-7 minutes
        logging.info("Scheduling scrolling every 5-7 minutes...")
        schedule.every(5).to(7).minutes.do(simulate_activity, driver=driver)

        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        logging.error(f"Error in main loop: {e}")
    finally:
        if driver:
            driver.quit()


def setup_chrome_options(headless=False):
    """Set up Chrome options for Selenium."""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-webgl")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--use-gl=swiftshader")
    chrome_options.add_argument("--disable-webgl2")
    chrome_options.add_argument("--disable-accelerated-2d-canvas")
    chrome_options.add_argument("--disable-accelerated-video-decode")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--ignore-gpu-blocklist")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    return chrome_options


def initialize_driver():
    """Initialize and return a Chrome WebDriver instance."""
    for attempt in range(RETRY_ATTEMPTS):
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=setup_chrome_options(headless=False),
            )
            return driver
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(RETRY_DELAY)
    raise Exception("Failed to initialize WebDriver after multiple attempts.")


# def scrape_article(url):
#     """Scrape an article and return its title, content, and URL."""
#     try:
#         logging.info(f"Scraping {url}...")
#         crawler = WebCrawler()
#         result = crawler.run(url)

#         # Extract title and content
#         title = result.get("title", "No Title")
#         content = result.get("content", "")

#         return title, content, url
#     except Exception as e:
#         logging.error(f"Error scraping {url}: {e}")
#         return None, None, None

def scrape_article(driver, url):
    """Scrape an article and return its title, content, and URL."""
    try:
        logging.info(f"Scraping {url}...")
        driver.get(url)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(random.uniform(10, 15))

        title = driver.title
        logging.info(f"Title: {title}")
        main_content = None

        # Try multiple selectors to extract main content
        selectors = ["article", "main", "div.content", "div.article", "div.post"]
        for selector in selectors:
            try:
                main_content = driver.find_element(
                    By.TAG_NAME if selector in ["article", "main"] else By.CSS_SELECTOR, selector
                ).text
                break
            except:
                continue

        if not main_content:
            main_content = driver.find_element(By.TAG_NAME, "body").text

        return title, main_content, url
    except Exception as e:
        logging.error(f"Error scraping {url}: {e}")
        return None, None, None

def preprocess_text(text):
    """Preprocess text to remove irrelevant content."""
    lines = text.splitlines()
    cleaned_lines = [line for line in lines if len(line.strip()) > 50]
    return "\n".join(cleaned_lines)


def summarize_text(text):
    """Summarize text using the DeepSeek API."""
    if not text:
        logging.error("Received empty text for summarization!")
        return None
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system",
                 "content": "You are a helpful assistant that summarizes text concisely for twitter posts. Don't make texts longer than 220 characters. Don't use hashtags."},
                {"role": "user",
                 "content": f"Summarize the following text for twitter post in 220 characters or less, don't use hashtags, don't make them longer than 220 characters.: {text}"},
            ],
            "max_tokens": 200,
            "stream": False,
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes

        summary = response.json()["choices"][0]["message"]["content"]
        return summary
    except Exception as e:
        logging.error(f"Error while summarizing text with DeepSeek API: {e}")
        return None


def scrape_and_summarize(driver, url):
    """Scrape an article and summarize its content."""
    title, text, link = scrape_article(driver, url)
    if not title or not text or not link:
        logging.error(f"Failed to scrape article from {url}.")
        return None, None, None

    # Preprocess text to remove irrelevant content
    cleaned_text = preprocess_text(text)

    # Summarize the cleaned text
    summary = summarize_text(cleaned_text)
    if not summary:
        logging.error(f"Failed to summarize article from {url}.")
        return None, None, None

    return title, summary, link


def save_cookies(driver):
    """Save cookies only after confirming login."""
    try:
        # Check that login has succeeded
        if is_logged_in(driver):
            cookies = driver.get_cookies()
            with open("twitter_cookies.pkl", "wb") as file:
                pickle.dump(cookies, file)
            logging.info("Cookies saved successfully.")
        else:
            logging.error("Cannot save cookies, user not logged in.")
    except Exception as e:
        logging.error(f"Error saving cookies: {e}")


def load_cookies(driver):
    """Load cookies from a file and add them to the driver."""
    if os.path.exists("twitter_cookies.pkl"):
        with open("twitter_cookies.pkl", "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        logging.info("Cookies loaded successfully.")

        driver.get("https://twitter.com/home")
        time.sleep(random.uniform(3, 5))
        if not is_logged_in(driver):
            logging.warning("Cookies seem invalid. Proceeding with fresh login.")
            return False  # Cookies are invalid
        return True
    else:
        logging.info("No cookies found. Proceeding with login.")
        return False


def handle_post_login(driver):
    """Handle potential post-login verification steps."""
    try:
        # Check if CAPTCHA or confirmation prompt exists
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='challenge_response']"))
        )
        logging.info("Additional verification required. Entering email...")
        challenge_input = driver.find_element(By.XPATH, "//input[@name='challenge_response']")
        challenge_input.send_keys(TWITTER_MAIL + Keys.RETURN)
        time.sleep(5)
    except:
        logging.info("No additional verification required.")


def login_to_twitter(driver):
    """Log in to Twitter and save cookies."""
    logging.info("Logging into Twitter...")
    driver.get("https://twitter.com/login")
    time.sleep(random.uniform(3, 5))

    try:
        username_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username_input.send_keys(TWITTER_USERNAME + Keys.RETURN)
        time.sleep(random.uniform(2, 5))

        # Handle additional confirmation step (if present)
        confirmation_elements = driver.find_elements(By.NAME, "text")
        if confirmation_elements:
            logging.info("Additional confirmation step detected. Entering email...")
            confirmation_elements[0].send_keys(TWITTER_MAIL + Keys.RETURN)
            time.sleep(random.uniform(2, 5))

        password_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(TWITTER_PASSWORD + Keys.RETURN)
        time.sleep(random.uniform(5, 10))

        time.sleep(20)
        handle_post_login(driver)
        # Check for incorrect login (e.g., incorrect password error or login still in form state)
        if "login" in driver.current_url:
            logging.error("Login failed. Please check your credentials.")
            return False  # Exit early

        # Save cookies only if login succeeded
        save_cookies(driver)
        return True
    except Exception as e:
        logging.error(f"Error during Twitter login: {e}")
        return False


def is_logged_in(driver):
    """Check if the user is logged in by looking for the presence of the profile icon."""
    try:
        driver.get("https://twitter.com/home")  # Navigate to the homepage
        time.sleep(random.uniform(3, 5))

        # Check for the presence of the profile icon (usually `aria-label="Profile"` exists when logged in)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="react-root"]/div/div/div[2]/header/div/div/div/div[2]/div/button'))
        )
        logging.info("Login successful as the profile icon is displayed.")
        return True
    except Exception as e:
        logging.error(f"Error detecting login status: {e}")
        return False


def simulate_activity(driver):
    """Simulate activity by scrolling the page."""
    try:
        logging.info("Simulating activity by scrolling...")

        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))

        # Scroll up
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(2, 4))
    except Exception as e:
        logging.error(f"Error simulating activity: {e}")


def post_tweet(driver, text):
    """Post a tweet using Selenium."""
    try:
        # Ensure login state is checked once in the main loop
        logging.info("Navigating to tweet box...")
        driver.get("https://twitter.com/compose/tweet")
        time.sleep(random.uniform(5, 10))

        tweet_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='textbox']"))
        )
        tweet_box.send_keys(text)
        time.sleep(random.uniform(2, 4))

        tweet_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id=\"layers\"]/div[2]/div/div/div/div/div/div[2]/div[2]"
                                                      "/div/div/div/div[3]/div[2]/div[1]/div/div/div/div[2]/div[2]"
                                                      "/div/div/div/button[2]"))
        )
        if not tweet_button.is_enabled():
            logging.error("Post button is disabled. Skipping this tweet.")
            return

        tweet_button.click()
        logging.info("Tweet posted successfully!")
        time.sleep(random.uniform(3, 6))
    except Exception as e:
        logging.error(f"Error posting tweet: {e}")


def load_posted_articles():
    """Load the set of already posted articles from a file."""
    if os.path.exists("posted_articles.txt"):
        with open("posted_articles.txt", "r") as file:
            return set(file.read().splitlines())
    return set()


def save_posted_article(link):
    """Save a newly posted article's link to the file."""
    try:
        with open("posted_articles.txt", "a") as file:
            file.write(link.strip() + "\n")
    except Exception as e:
        logging.error(f"Failed to save article: {e}")


def filter_article(title, content):
    """Filter articles based on keywords to ensure relevance."""
    KEYWORDS = ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "LLM", "GPT", "Reasoning",
                "Quantum"]
    return any(keyword.lower() in title.lower() or keyword.lower() in content.lower() for keyword in KEYWORDS)


def job(driver, posted_articles):
    """Main job: Scrape, summarize, and tweet."""
    try:
        # Randomize the order of sources
        sources = NEWS_SOURCES.copy()
        random.shuffle(sources)

        for source in sources:
            logging.info(f"Processing source: {source}")
            title, content, link = scrape_article(driver, source)
            if not title or not content or not link:
                logging.error(f"Failed to scrape article from {source}. Skipping...")
                continue

            cleaned_text = preprocess_text(content)
            summary = summarize_text(cleaned_text)

            if link not in posted_articles:
                post_tweet(driver, summary[:MAX_TWEET_LENGTH])
                posted_articles.add(link)
                save_posted_article(link)
                delay = random.uniform(600, 900)
                logging.info(f"Article posted successfully! Sleeping for {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error(f"Article already posted: {link}")


        if len(posted_articles) >= len(NEWS_SOURCES):
            logging.info("All sources have been processed. Deleting posted_articles.txt...")
            if os.path.exists("posted_articles.txt"):
                os.remove("posted_articles.txt")
                logging.info("posted_articles.txt deleted.")
            posted_articles.clear()  # Clear the set for the next cycle


    except Exception as e:
        logging.error(f"Error in job function: {e}")


def signal_handler(sig, frame):
    """Handle script interruption (e.g., Ctrl+C)."""
    logging.info("Script interrupted. Shutting down...")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()