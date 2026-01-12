import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Keys
    groq_api_key: str = ""
    huggingface_api_key: str = ""
    
    # Security
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Application
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Server
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8000"))  # Render sets PORT dynamically
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()