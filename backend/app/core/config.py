"""
Application Configuration

Manages environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Project Info
    PROJECT_NAME: str = "DiagnoLeads API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API Settings
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Database (Supabase PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/diagnoleads"

    # Redis (Upstash)
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # Anthropic Claude API
    ANTHROPIC_API_KEY: str = ""

    # Trigger.dev
    TRIGGER_API_KEY: str = ""
    TRIGGER_API_URL: str = "https://api.trigger.dev"

    # External Integrations (Optional)
    SALESFORCE_CLIENT_ID: str = ""
    SALESFORCE_CLIENT_SECRET: str = ""
    HUBSPOT_API_KEY: str = ""
    SLACK_WEBHOOK_URL: str = ""

    # Microsoft Teams Integration
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = ""
    BOT_APP_ID: str = ""
    BOT_APP_PASSWORD: str = ""
    TEAMS_WEBHOOK_URL: str = ""

    # Email Settings (SMTP)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@diagnoleads.com"
    FROM_NAME: str = "DiagnoLeads"

    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
