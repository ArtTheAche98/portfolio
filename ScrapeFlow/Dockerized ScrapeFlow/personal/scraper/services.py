import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ContentOptimizer:
    def __init__(self):
        api_key = os.getenv('DEEPSEEK_API_KEY')
        base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
        
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=None
        )

    def optimize_content(self, content, style='INSIGHTS'):
        """Optimize content using DeepSeek AI"""
        style_prompts = {
            'NEWS': "Transform this content into a professional news-style LinkedIn post:",
            'INSIGHTS': "Extract key industry insights from this content and create an engaging LinkedIn post:",
            'SUMMARY': "Create a concise summary of this content for LinkedIn:",
            'QUOTES': "Extract and highlight key quotes and insights from this content for LinkedIn:"
        }

        prompt = style_prompts.get(style, style_prompts['INSIGHTS'])
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a professional content optimizer for LinkedIn."},
                    {"role": "user", "content": f"{prompt}\n\n{content}"}
                ],
                max_tokens=500,
                temperature=0.7
            )
            optimized_content = response.choices[0].message.content
            # Remove markdown formatting
            optimized_content = optimized_content.replace('**', '').replace('*', '')
            return optimized_content
        except Exception as e:
            print(f"Error optimizing content: {str(e)}")
            return None