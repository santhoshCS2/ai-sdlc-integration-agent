import os
from groq import Groq
import logging

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)

    def _generate_completion(self, prompt: str, system_prompt: str = "You are a professional software architect.") -> str:
        if not self.client:
            return None
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.5,
                max_tokens=4096,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return None
