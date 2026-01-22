"""
Application configuration and settings
Loads environment variables from .env file
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API Settings
    api_title: str = "Game Survey Analyzer"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Gemini API
    gemini_api_key: str = ""  # Must be set in .env
    
    # File Upload Settings
    max_file_size_mb: int = 5
    allowed_file_types: str = "csv,xlsx"
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = False
    
    def get_max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024


# Create singleton instance
settings = Settings()
