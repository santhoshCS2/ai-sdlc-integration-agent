from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, agents
from app.core.database import engine, Base
from app.core.config import settings
import functools

# Global patch for OpenAI/Groq 'reasoning_format' error
def patch_llm_reasoning():
    def strip_unsupported_params(kwargs):
        # Strip parameters that cause TypeError in older/modified client versions or specific providers
        unsupported = ["reasoning_format", "reasoning_effort", "service_tier"]
        for key in unsupported:
            if key in kwargs:
                kwargs.pop(key)
        return kwargs

    def create_patch(original_func):
        @functools.wraps(original_func)
        def patched_func(*args, **kwargs):
            return original_func(*args, **strip_unsupported_params(kwargs))
        return patched_func

    # Patch OpenAI
    try:
        import openai.resources.chat.completions as chat_completions
        chat_completions.Completions.create = create_patch(chat_completions.Completions.create)
        chat_completions.AsyncCompletions.create = create_patch(chat_completions.AsyncCompletions.create)
    except (ImportError, AttributeError):
        pass

    # Patch Groq
    try:
        import groq.resources.chat.completions as groq_completions
        groq_completions.Completions.create = create_patch(groq_completions.Completions.create)
        groq_completions.AsyncCompletions.create = create_patch(groq_completions.AsyncCompletions.create)
    except (ImportError, AttributeError):
        pass

patch_llm_reasoning()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SDLC Agent Backend")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])

@app.get("/")
def read_root():
    return {"message": "Welcome to SDLC Agent API"}

@app.get("/api/test")
def test_endpoint():
    return {"status": "Backend is working", "timestamp": "2025-01-24"}
