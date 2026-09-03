"""
LEVELLY — Application Configuration
Uses pydantic-settings for environment variable loading
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Application
    APP_ENV: str = "development"
    APP_NAME: str = "LEVELLY"
    SECRET_KEY: str = "change-this-secret-key-in-production-minimum-32-chars"
    JWT_SECRET: str = "change-this-jwt-secret-in-production-minimum-32-chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Database
    DATABASE_URL: str = "postgresql://levelly:levelly123@localhost:5432/levelly_db"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    FRONTEND_URL: str = "http://localhost:5173"

    # Groq AI Coach
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # Partner configuration
    PAYMENT_PROVIDER: str = "mock"
    PAYMENT_PROVIDER_API_URL: Optional[str] = None
    PAYMENT_PROVIDER_KEY: Optional[str] = None
    PAYMENT_PROVIDER_SECRET: Optional[str] = None

    NBFC_PROVIDER: str = "mock"
    INVESTMENT_PROVIDER: str = "mock"
    NBFC_API_URL: Optional[str] = None
    NBFC_API_KEY: Optional[str] = None
    INVESTMENT_API_URL: Optional[str] = None
    INVESTMENT_API_KEY: Optional[str] = None

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Financial engine thresholds (configurable)
    DISTRESS_LOW_MAX: int = 30
    DISTRESS_MODERATE_MAX: int = 60
    DISTRESS_HIGH_MAX: int = 80
    # Above 80 = SEVERE

    # Income intelligence windows
    INCOME_RECENT_DAYS: int = 28
    INCOME_HISTORICAL_MONTHS: int = 3

    # Volatility classification
    VOLATILITY_LOW_MAX: float = 0.15
    VOLATILITY_MODERATE_MAX: float = 0.30
    # Above 0.30 = HIGH

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
