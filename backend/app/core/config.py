"""
Application Configuration

Manages environment variables and application settings.
環境別の設定（development, staging, production）を適切に管理します。
"""

from functools import lru_cache
from typing import List, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # ========================================================================
    # Project Info
    # ========================================================================
    PROJECT_NAME: str = "DiagnoLeads API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    DEBUG: bool = True

    # ========================================================================
    # API Settings
    # ========================================================================
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ========================================================================
    # CORS
    # ========================================================================
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # ========================================================================
    # Database (Supabase PostgreSQL)
    # ========================================================================
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/diagnoleads"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False  # SQLAlchemy logging

    # ========================================================================
    # Redis (Upstash)
    # ========================================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_SOCKET_TIMEOUT: int = 5

    # ========================================================================
    # JWT Authentication
    # ========================================================================
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """本番環境でデフォルトのシークレットキーを使用していないか検証"""
        if info.data.get("ENVIRONMENT") == "production":
            if v == "your-secret-key-change-this-in-production":
                raise ValueError("本番環境でデフォルトのSECRET_KEYを使用しています。" "必ず強力なランダムキーに変更してください。")
        return v

    # ========================================================================
    # Supabase
    # ========================================================================
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # ========================================================================
    # Anthropic Claude API
    # ========================================================================
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_API_TIMEOUT: int = 60  # seconds
    ANTHROPIC_MAX_RETRIES: int = 3

    # ========================================================================
    # Trigger.dev
    # ========================================================================
    TRIGGER_API_KEY: str = ""
    TRIGGER_API_URL: str = "https://api.trigger.dev"

    # ========================================================================
    # External Integrations (Optional)
    # ========================================================================
    SALESFORCE_CLIENT_ID: str = ""
    SALESFORCE_CLIENT_SECRET: str = ""
    HUBSPOT_API_KEY: str = ""
    SLACK_WEBHOOK_URL: str = ""

    # ========================================================================
    # Microsoft Teams Integration
    # ========================================================================
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = ""
    BOT_APP_ID: str = ""
    BOT_APP_PASSWORD: str = ""
    TEAMS_WEBHOOK_URL: str = ""

    # ========================================================================
    # Email Settings (SMTP)
    # ========================================================================
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@diagnoleads.com"
    FROM_NAME: str = "DiagnoLeads"

    # Frontend URL (for email links)
    FRONTEND_URL: str = "http://localhost:5173"

    # ========================================================================
    # Security
    # ========================================================================
    BCRYPT_ROUNDS: int = 12
    PASSWORD_MIN_LENGTH: int = 8

    # ========================================================================
    # Rate Limiting
    # ========================================================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # ========================================================================
    # Logging
    # ========================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text

    # ========================================================================
    # File Upload
    # ========================================================================
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".pdf", ".csv"]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 未定義の環境変数を無視

    @property
    def is_production(self) -> bool:
        """本番環境かどうかを判定"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """開発環境かどうかを判定"""
        return self.ENVIRONMENT == "development"

    @property
    def is_staging(self) -> bool:
        """ステージング環境かどうかを判定"""
        return self.ENVIRONMENT == "staging"


@lru_cache()
def get_settings() -> Settings:
    """
    設定のシングルトンインスタンスを取得

    キャッシュされるため、アプリケーション起動後は同じインスタンスが返される
    """
    return Settings()


# グローバル設定インスタンス
settings = get_settings()
