"""
Smart Village Management System - Configuration Settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator
import secrets


class Settings(BaseSettings):
    # Project Information
    PROJECT_NAME: str = "Smart Village Management System API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for Smart Village Management System"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    @validator("ALLOWED_HOSTS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    DATABASE_URL: str = "postgresql://admin:password123@localhost:5432/smart_village"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_EXPIRE_SECONDS: int = 3600
    
    # LINE Integration
    LINE_CHANNEL_ID: str = ""
    LINE_CHANNEL_SECRET: str = ""
    LINE_CHANNEL_ACCESS_TOKEN: str = ""
    LINE_LIFF_ID: str = ""
    
    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
    UPLOAD_DIR: str = "uploads"
    
    # External APIs
    BANKING_API_URL: str = ""
    BANKING_API_KEY: str = ""
    OCR_API_URL: str = ""
    OCR_API_KEY: str = ""
    
    # ISAPI Device Integration
    ISAPI_USERNAME: str = "admin"
    ISAPI_PASSWORD: str = ""
    ISAPI_TIMEOUT: int = 30
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Development/Production
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    @validator("DEBUG", pre=True)
    def set_debug_mode(cls, v, values):
        return values.get("ENVIRONMENT", "development") == "development"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    # Session Configuration
    SESSION_EXPIRE_SECONDS: int = 86400  # 24 hours
    
    # Audit Logging
    ENABLE_AUDIT_LOG: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 365
    
    # Backup Configuration
    BACKUP_ENABLED: bool = True
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields from .env


# Create settings instance
settings = Settings()


# Database URL for different environments
def get_database_url() -> str:
    """Get database URL based on environment"""
    if settings.ENVIRONMENT == "production":
        # Production database URL should be set via environment variable
        return settings.DATABASE_URL
    elif settings.ENVIRONMENT == "staging":
        # Staging database URL
        return settings.DATABASE_URL
    else:
        # Development database URL
        return settings.DATABASE_URL


# Redis URL for different environments
def get_redis_url() -> str:
    """Get Redis URL based on environment"""
    if settings.ENVIRONMENT == "production":
        return settings.REDIS_URL
    elif settings.ENVIRONMENT == "staging":
        return settings.REDIS_URL
    else:
        return settings.REDIS_URL

