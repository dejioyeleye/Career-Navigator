from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Skill-Bridge Career Navigator"
    app_env: str = "dev"
    database_url: str = "sqlite:///./skillbridge.db"
    
    # AI Configuration
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-4o-mini"
    ai_timeout_seconds: int = 5
    
    # Gemini API (Primary AI)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    gemini_timeout: int = 30
    use_static_mvp: bool = False
    
    # Security Settings
    allowed_origins: str = "http://localhost:3000"
    rate_limit_per_minute: int = 10
    max_resume_size_mb: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
