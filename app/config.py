"""
Application configuration using Pydantic Settings.

Configuration is loaded from environment variables with support for
default values and .env file loading.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    app_name: str = "myTomorrows CRM API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: Optional[int] = None
    
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    @property
    def get_database_url(self) -> str:
        """Construct database URL from POSTGRES_* variables."""
        user = self.postgres_user or os.getenv("POSTGRES_USER", "mytomorrows")
        password = self.postgres_password or os.getenv("POSTGRES_PASSWORD", "mytomorrows123")
        host = self.postgres_host or os.getenv("POSTGRES_HOST", "localhost")
        port = self.postgres_port or int(os.getenv("POSTGRES_PORT", "5432"))
        db = self.postgres_db or os.getenv("POSTGRES_DB", "mytomorrows_db")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"


settings = Settings()
