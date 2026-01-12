from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, agents
from app.core.database import engine, Base
from app.core.config import settings

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
