"""
Configuration settings for the GoWombat Doodles Generator.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    gemini_model: str = "google/gemini-2.5-flash-image-preview:free"
    
    app_name: str = "GoWombat Doodles Generator"
    app_version: str = "1.0.0"
    debug: bool = False
    
    cors_origins: list[str] = ["*"]
    
    max_prompt_length: int = 500
    image_generation_timeout: int = 60
    
    rate_limit_requests: int = 10
    rate_limit_period: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings
    """
    return Settings()