"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # AI Provider
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    consent_token_expire_minutes: int = 15

    # Similarity Thresholds
    name_similarity_threshold: float = 0.85
    address_similarity_threshold: float = 0.80
    overall_match_threshold: float = 0.82

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
