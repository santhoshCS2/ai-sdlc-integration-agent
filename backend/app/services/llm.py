from app.core.config import settings
from app.core.llm.llm_with_fallback import LLMWithFallback
from langchain_core.messages import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Initialize robust LLM with automatic fallback
        try:
            self.llm = LLMWithFallback(api_key=settings.GROQ_API_KEY)
            self.has_key = bool(settings.GROQ_API_KEY or settings.OPENROUTER_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize LLM core: {e}")
            self.llm = None
            self.has_key = False

    async def get_response(self, prompt: str, system_prompt: str = "You are a professional SDLC Agent assistant. Provide concise, expert-level advice.") -> str:
        if not self.has_key:
            return "Error: API keys not configured. Please add GROQ_API_KEY or OPENROUTER_API_KEY to your .env file."

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ]
            
            # Using invoke which handles rotation internally
            response = self.llm.invoke(messages)
            
            return response.content if hasattr(response, 'content') else str(response)
                    
        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"LLM Processing Error: {e}")
            
            if "credits" in error_str or "quota" in error_str:
                 return "I apologize, but we have hit a usage limit with the AI provider. Please check your plan or API key credits."
            
            return f"I apologize, but I'm having trouble connecting to my intelligence core right now. (System Error: {str(e)[:100]})"

llm_service = LLMService()
