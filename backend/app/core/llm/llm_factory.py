"""
Factory for creating LLM instances with multiple providers.

PRIMARY: Groq (free and fast - always tried first)
FALLBACK: OpenRouter (only used if Groq is not available)

Also supports OpenAI and Anthropic when explicitly provided.
"""

from typing import Optional
import os

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
import functools


class LLMFactory:
    """Factory for creating LLM instances (OpenRouter, Groq, OpenAI, Anthropic)."""

    # OpenRouter model options (access to multiple providers)
    OPENROUTER_MODELS = {
        "openai/gpt-4o": "GPT-4 Omni - Latest and most capable (recommended)",
        "openai/gpt-4-turbo": "GPT-4 Turbo - Fast and capable",
        "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet - Excellent reasoning",
        "google/gemini-pro-1.5": "Gemini Pro 1.5 - Great for code generation",
        "meta-llama/llama-3.1-70b-instruct": "Llama 3.1 70B - Open source powerhouse",
        "mistralai/mixtral-8x7b-instruct": "Mixtral 8x7B - Fast and efficient",
    }

    DEFAULT_MODEL = "openai/gpt-4o"

    # Groq model options
    GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"
    GROQ_FALLBACK_MODELS = [
        "llama-3.1-70b-versatile", # Sometimes available when 3.3 is not
        "llama-3.1-8b-instant",    # Very fast, high limit
        "mixtral-8x7b-32768",      # Good fallback
        "llama3-8b-8192",          # Reliable old model
    ]
    
    # Note: API keys are loaded from .env file or environment variables
    # OPENROUTER_API_KEY (PRIMARY) and GROQ_API_KEY (FALLBACK)

    @staticmethod
    def _create_openrouter_llm(api_key: str, model: Optional[str] = None):
        """Create an LLM that talks to OpenRouter via OpenAI-compatible API."""
        # Use a cheaper model for free tier when no explicit model requested
        selected_model = model or LLMFactory.DEFAULT_MODEL
        if not model and selected_model == LLMFactory.DEFAULT_MODEL:
            selected_model = "meta-llama/llama-3.1-70b-instruct"

        return ChatOpenAI(
            model=selected_model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/your-repo",  # Optional: for analytics
                "X-Title": "FigmaToFullApp",  # Optional: for analytics
            },
            temperature=0.7,
            max_tokens=16000,  # Increased for complete code generation (can generate full backends)
            timeout=120,  # Longer timeout for code generation
        )

    @staticmethod
    def _create_groq_llm(api_key: str, model: Optional[str] = None):
        """Create an LLM that talks to Groq."""
        # Always use the latest model - ensure we never use the decommissioned model
        selected_model = model or LLMFactory.GROQ_DEFAULT_MODEL
        
        # Safety check: ensure we're not using the old decommissioned model
        if selected_model == "llama-3.1-70b-versatile":
            selected_model = LLMFactory.GROQ_DEFAULT_MODEL
        
        return ChatGroq(
            model=selected_model,
            api_key=api_key,
            temperature=0.7,
            max_tokens=4000,
            timeout=120,
        )

    @staticmethod
    def create_llm(api_key: Optional[str] = None, model: Optional[str] = None) -> any:
        """
        Create an LLM instance with Groq as PRIMARY and OpenRouter as FALLBACK:
        
        Priority order:
        1. Environment GROQ_API_KEY → PRIMARY (free and fast)
        2. Environment OPENROUTER_API_KEY → FALLBACK (only if Groq not available)
        3. Explicit keys override environment variables
        
        Other providers (OpenAI, Anthropic) are supported if explicitly provided.
        """
        # Check environment variables
        env_openrouter_key = os.getenv("OPENROUTER_API_KEY")
        env_groq_key = os.getenv("GROQ_API_KEY")
        
        # If an explicit API key is provided, detect its type
        if api_key:
            api_key = api_key.strip()

            # OpenRouter keys start with sk-or-v1- (FALLBACK - only if Groq not available)
            if api_key.startswith("sk-or-v1-") or (api_key.startswith("sk-") and len(api_key) > 100):
                # Still try Groq first if available from environment
                if env_groq_key:
                    return LLMFactory._create_groq_llm(env_groq_key, model)
                return LLMFactory._create_openrouter_llm(api_key, model)

            # Groq keys start with gsk_ (PRIMARY - use immediately)
            if api_key.startswith("gsk_"):
                return LLMFactory._create_groq_llm(api_key, model)

            # Standard OpenAI keys (sk-... ~50 chars)
            if api_key.startswith("sk-") and len(api_key) < 60:
                return ChatOpenAI(
                    model=model or "gpt-4-turbo-preview",
                    api_key=api_key,
                    temperature=0.7,
                )

            # Anthropic keys start with sk-ant-
            if api_key.startswith("sk-ant-"):
                return ChatAnthropic(
                    model=model or "claude-3-5-sonnet-20241022",
                    api_key=api_key,
                    temperature=0.7,
                )

            # Unknown pattern - prefer OpenRouter (PRIMARY)
            return LLMFactory._create_openrouter_llm(api_key, model)

        # No explicit key provided -> PRIMARY: OpenRouter (updated with credits), FALLBACK: Groq
        # Priority 1: Environment OpenRouter key (updated with credits)
        if env_openrouter_key:
            return LLMFactory._create_openrouter_llm(env_openrouter_key, model)
        
        # Priority 2: Environment Groq key (FALLBACK - free backup)
        if env_groq_key:
            return LLMFactory._create_groq_llm(env_groq_key, model)
        
        # Last resort: raise error if no keys are configured
        raise ValueError(
            "No API keys found! Please set GROQ_API_KEY (recommended - free) or OPENROUTER_API_KEY in your .env file or environment variables."
        )

    @staticmethod
    def create_fallback_groq_llm(api_key: str, attempt_index: int) -> any:
        """Create a fallback Groq LLM based on attempt index."""
        if attempt_index < len(LLMFactory.GROQ_FALLBACK_MODELS):
            model = LLMFactory.GROQ_FALLBACK_MODELS[attempt_index]
            return LLMFactory._create_groq_llm(api_key, model)
        return None

    @staticmethod
    def get_models() -> dict:
        """Get available OpenRouter models (for UI display)."""
        return LLMFactory.OPENROUTER_MODELS
