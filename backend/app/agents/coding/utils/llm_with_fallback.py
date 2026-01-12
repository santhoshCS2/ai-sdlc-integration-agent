"""
LLM wrapper with automatic fallback from Groq to OpenRouter on errors.
"""

from typing import Optional, Any, List
from langchain_core.messages import BaseMessage
from utils.llm_factory import LLMFactory
import os


class LLMWithFallback:
    """
    LLM wrapper that automatically falls back to OpenRouter if Groq fails.
    Handles rate limits, invalid keys, and other API errors.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.primary_llm = None
        self.fallback_llm = None
        self.using_fallback = False
        self._initialize_llms()
    
    def _initialize_llms(self):
        """Initialize both primary (Groq) and fallback (OpenRouter) LLMs"""
        # Get keys from environment
        env_openrouter_key = os.getenv("OPENROUTER_API_KEY")
        env_groq_key = os.getenv("GROQ_API_KEY")
        
        # Initialize primary LLM (OpenRouter - updated with credits)
        try:
            if self.api_key and (self.api_key.startswith("sk-or-v1-") or (self.api_key.startswith("sk-") and len(self.api_key) > 100)):
                self.primary_llm = LLMFactory._create_openrouter_llm(self.api_key, self.model)
            elif env_openrouter_key:
                self.primary_llm = LLMFactory._create_openrouter_llm(env_openrouter_key, self.model)
            else:
                # No OpenRouter key, skip primary
                self.primary_llm = None
        except Exception as e:
            # If initialization fails, skip primary
            self.primary_llm = None
        
        # Initialize fallback LLM (Groq)
        try:
            if self.api_key and self.api_key.startswith("gsk_"):
                self.fallback_llm = LLMFactory._create_groq_llm(self.api_key, self.model)
            elif env_groq_key:
                self.fallback_llm = LLMFactory._create_groq_llm(env_groq_key, self.model)
            else:
                self.fallback_llm = None
        except Exception as e:
            self.fallback_llm = None
    
    def _should_fallback(self, error: Exception) -> bool:
        """Determine if we should fall back to Groq based on the error"""
        error_str = str(error).lower()
        
        # Check for specific error codes that indicate we should fallback
        fallback_indicators = [
            "402",  # Insufficient credits
            "401",  # Invalid API key
            "429",  # Rate limit
            "requires more credits",
            "can only afford",
            "insufficient credits",
            "invalid_api_key",
            "rate limit",
        ]
        
        return any(indicator in error_str for indicator in fallback_indicators)
    
    def invoke(self, messages: List[BaseMessage], **kwargs) -> Any:
        """
        Invoke LLM with automatic fallback to Groq if OpenRouter fails.
        """
        # Try primary LLM first (OpenRouter)
        if self.primary_llm and not self.using_fallback:
            try:
                # Use a copy of kwargs to avoid modifying the original
                invoke_kwargs = kwargs.copy()
                # Only set default max_tokens if not explicitly provided
                # This allows code generators to request higher limits
                if 'max_tokens' not in invoke_kwargs:
                    invoke_kwargs['max_tokens'] = 16000  # Higher default for complete code generation
                
                response = self.primary_llm.invoke(messages, **invoke_kwargs)
                return response
            except Exception as e:
                # Check if we should fallback
                if self._should_fallback(e) and self.fallback_llm:
                    # Switch to fallback
                    self.using_fallback = True
                    # Retry with Groq
                    try:
                        response = self.fallback_llm.invoke(messages, **kwargs)
                        return response
                    except Exception as fallback_error:
                        # Both failed, raise the original error
                        raise e
                else:
                    # Don't fallback for this error, or no fallback available
                    raise e
        
        # If already using fallback or no primary LLM, use fallback directly
        if self.fallback_llm:
            try:
                response = self.fallback_llm.invoke(messages, **kwargs)
                return response
            except Exception as e:
                raise e
        
        # No LLMs available
        raise ValueError("No LLM available. Please set GROQ_API_KEY (recommended - free) or OPENROUTER_API_KEY in your .env file.")
    
    def __getattr__(self, name):
        """Delegate other method calls to the active LLM"""
        active_llm = self.fallback_llm if self.using_fallback else self.primary_llm
        if active_llm is None:
            active_llm = self.fallback_llm or self.primary_llm
        
        if active_llm is None:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        return getattr(active_llm, name)

