"""
Configuration settings for the Mock Interview System
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Mock Interview AI System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/mock_interview_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".doc", ".docx"}
    
    # Job Search API (Mock for now)
    JOB_API_BASE_URL: str = "https://api.adzuna.com/v1/api"
    JOB_API_KEY: Optional[str] = None
    JOB_API_ID: Optional[str] = None
    
    # External APIs
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v):
        if isinstance(v, str):
            return v
        raise ValueError("DATABASE_URL must be a string")
    
    @validator("OPENAI_API_KEY", pre=True)
    def validate_openai_key(cls, v):
        if v is None:
            print("⚠️  OPENAI_API_KEY not set. AI features will be limited.")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
