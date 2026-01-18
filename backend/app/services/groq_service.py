import os
import logging
from app.core.config import settings
from app.core.llm.llm_with_fallback import LLMWithFallback
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

class GroqService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        if not self.api_key and not settings.OPENROUTER_API_KEY:
            logger.warning("No API keys found in environment for GroqService")
            self.llm = None
        else:
            # Use centralized fallback wrapper
            try:
                self.llm = LLMWithFallback(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize GroqService LLM: {e}")
                self.llm = None

    def _generate_completion(self, prompt: str, system_prompt: str = "You are a professional software architect.") -> str:
        if not self.llm:
            return None
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            logger.error(f"Groq/LLM Error in _generate_completion: {str(e)}")
            return None
