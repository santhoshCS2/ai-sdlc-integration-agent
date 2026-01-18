"""
LLM wrapper with automatic fallback from Groq to OpenRouter on errors.
"""

from typing import Optional, Any, List
from langchain_core.messages import BaseMessage
from app.core.llm.llm_factory import LLMFactory
import os


class LLMWithFallback:
    """
    LLM wrapper that automatically falls back to OpenRouter if Groq fails.
    Handles rate limits, invalid keys, and other API errors.
    Also rotates through multiple Groq models if the primary Groq model hit rate limits.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.primary_llm = None
        self.fallback_llm = None
        self.using_fallback = False
        
        # Store keys for dynamic fallback model creation
        self.env_openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.env_groq_key = os.getenv("GROQ_API_KEY")
        
        self._initialize_llms()
    
    def _initialize_llms(self):
        """Initialize both primary (OpenRouter) and fallback (Groq) LLMs"""
        # Initialize primary LLM (OpenRouter - updated with credits)
        try:
            if self.api_key and (self.api_key.startswith("sk-or-v1-") or (self.api_key.startswith("sk-") and len(self.api_key) > 100)):
                self.primary_llm = LLMFactory._create_openrouter_llm(self.api_key, self.model)
            elif self.env_openrouter_key:
                self.primary_llm = LLMFactory._create_openrouter_llm(self.env_openrouter_key, self.model)
            else:
                self.primary_llm = None
        except Exception:
            self.primary_llm = None
        
        # Initialize fallback LLM (Groq)
        try:
            if self.api_key and self.api_key.startswith("gsk_"):
                self.fallback_llm = LLMFactory._create_groq_llm(self.api_key, self.model)
            elif self.env_groq_key:
                self.fallback_llm = LLMFactory._create_groq_llm(self.env_groq_key, self.model)
            else:
                self.fallback_llm = None
        except Exception:
            self.fallback_llm = None
    
    def _should_fallback(self, error: Exception) -> bool:
        """Determine if we should fall back to Groq based on the error"""
        error_str = str(error).lower()
        
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
        Invoke LLM with automatic fallback logic:
        1. Try OpenRouter (Primary)
        2. If OR fails (credits/rate limit), try Groq (Fallback)
        3. If Groq hits rate limit (429), rotate through alternative Groq models
        """
        # Try primary LLM first (OpenRouter)
        if self.primary_llm and not self.using_fallback:
            try:
                invoke_kwargs = kwargs.copy()
                if 'max_tokens' not in invoke_kwargs:
                    invoke_kwargs['max_tokens'] = 16000
                
                return self.primary_llm.invoke(messages, **invoke_kwargs)
            except Exception as e:
                # Always allow rate limit fallback logic to run, even if it's the primary LLM
                pass
        
        # Logic for Groq (either as primary fallback or environment configured primary)
        # Check if we should use Groq logic (either falling back OR Groq keys are present and no OR key)
        use_groq = self.fallback_llm or (self.api_key and self.api_key.startswith("gsk_"))
        
        if use_groq:
            # Multi-model Groq rotation
            groq_key = self.api_key if (self.api_key and self.api_key.startswith("gsk_")) else self.env_groq_key
            
            # Start with the default Groq model, then try fallbacks
            for i in range(-1, len(LLMFactory.GROQ_FALLBACK_MODELS)):
                try:
                    current_llm = self.fallback_llm if i == -1 else LLMFactory.create_fallback_groq_llm(groq_key, i)
                    if not current_llm:
                        continue
                        
                    return current_llm.invoke(messages, **kwargs)
                except Exception as e:
                    error_str = str(e).lower()
                    if "429" in error_str and i < len(LLMFactory.GROQ_FALLBACK_MODELS) - 1:
                        model_name = getattr(current_llm, 'model_name', 'default')
                        print(f"📉 Groq rate limit hit for {model_name}. Trying next fallback model...")
                        continue
                    
                    raise e
        
        raise ValueError("No LLM available. Please check your API keys.")
    
    def __getattr__(self, name):
        """Delegate other method calls to the active LLM"""
        # If calling logic has set us to fallback mode, prefer fallback
        active_llm = self.fallback_llm if self.using_fallback else self.primary_llm
        if active_llm is None:
            active_llm = self.fallback_llm or self.primary_llm
        
        if active_llm is None:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        return getattr(active_llm, name)
