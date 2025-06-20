# Automated AI News Summarizer & Twitter Bot

## Project Overview

This is an **AI-powered News Summarizer and Twitter Bot** that automates the process of gathering AI-related news, summarizing it, and posting it directly to Twitter. The bot leverages **Python**, **Selenium**, and the **DeepSeek API** to perform web scraping, summarization, and Twitter interaction seamlessly.

---

## Why I Chose These Sources and Tools

### News Sources
This bot gathers information from trusted and authoritative sources in the field of artificial intelligence, including:
- [ArXiv](https://arxiv.org/)
- [OpenAI Blog](https://openai.com/blog)
- [Google AI Blog](https://ai.googleblog.com/)
- [DeepMind Blog](https://deepmind.com/blog)
- [Hugging Face Blog](https://huggingface.co/blog)
- [TechCrunch AI](https://techcrunch.com/category/artificial-intelligence/)
- [VentureBeat AI](https://venturebeat.com/category/ai/)
- [The Batch](https://www.deeplearning.ai/the-batch/)

These sources were selected to ensure the bot posts only high-quality and relevant information about advancements in AI and large language models (LLMs).

### Tools and Libraries

- **Python**: Used for its versatile ecosystem and extensive libraries that enable efficient web scraping, automation, and integration with APIs.
- **Selenium**: A web automation framework that enables scraping dynamic content and interacting directly with websites (e.g., logging into Twitter).
- **DeepSeek API**: Provides accurate text summarization, which allows the bot to condense AI-related news into concise summaries for tweets.

---

## Features

### 1. Web Scraping
The bot scrapes articles from specified AI-focused blogs and platforms using Selenium WebDriver. It employs customizable scraping logic and preprocessing to extract meaningful content.

### 2. Summarization
Using the DeepSeek API, the bot generates short and engaging summaries of the scraped content:
- Summaries are concise (under 220 characters).
- Only the most relevant details are shared in the post.

### 3. Twitter Automation
The bot automates interaction with Twitter for posting the summarized news:
- Automates the login process using either cookies or credentials.
- Posts directly to the user's Twitter timeline with the summarized content and source link.
- Simulates user activity such as scrolling to reduce bot detection.

### 4. Scheduling
The automation workflow is powered by the **`schedule`** library:
- Runs every 2 hours to scrape, summarize, and post news.
- Simulates user activity every 5-7 minutes.

---

## Setup Instructions

### 1. Prerequisites
- **Python 3.8+**
- Chrome browser and [ChromeDriver](https://chromedriver.chromium.org/)
- **Virtual Environment (Recommended)**: It's highly advisable to set up the project in a Python virtual environment to maintain a clean and isolated dependency setup.

### 2. Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ArtTheAche98/TwitterBot.git
   cd TwitterBot
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Required Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Environment Variables
Create a `.env` file in the project root and securely store your credentials and API keys in it:

```plaintext
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password
TWITTER_MAIL=your_twitter_email
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 4. Running the Bot

Start the bot by executing the following command:

```bash
python bot.py
```

### 5. Key Notes
- **Cookies**: Twitter session cookies are saved locally to avoid repeated logins in subsequent runs.
- **Error Logging**: Errors and status updates are logged to a file (`news_bot.log`) for easy monitoring and debugging.

---

## Challenges and Adaptations

During development, several challenges arose that required creative problem-solving:
- **Scraping Limitations**: To bypass blocks on some websites, techniques like proxies and rate limiting were utilized.
- **Twitter API Restrictions**: The bot switched to Selenium for direct interaction with Twitter, bypassing API limitations entirely.
- **Local System Limitations**: Instead of running a local model for summarization, the reliable and cost-effective DeepSeek API was used.

These challenges provided invaluable learning opportunities and significantly enhanced the robustness of the project.

---

## For Developers & Contributors

This repository is designed with extensibility in mind. Here are a few potential areas for improvement if you'd like to contribute:

1. **Add More Sources**
    - Integrate additional AI-related blogs or publications.
    - Implement RSS feed parsing for better scalability.

2. **Enhance Summarization**
    - Incorporate a more customizable summarization solution.
    - Optionally, fine-tune an LLM for niche AI content summarization.

3. **Expand Platform Support**
    - Extend the bot’s functionality to integrate other platforms like LinkedIn or Medium for broader sharing.

Contributions are welcome! Feel free to fork the repository and submit a pull request with your enhancements.

---

## Learning & Development Experience

This project was a great learning experience and a practical challenge. It taught me to work with:
- Web scraping tools and techniques.
- Automation using Selenium.
- API integration for summarization.
- Scheduling scripts for long-running automation.
- Working with VM.

---



## Acknowledgements

Special thanks to the developers of open-source tools and libraries that were instrumental in building this project.

---

## License

This project is open-source and available under the [MIT License](LICENSE).