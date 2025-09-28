"""Configuration settings for the Telegram Refuel Bot."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings."""
    
    # Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'refuel_bot')
    DB_USER = os.getenv('DB_USER', 'refuel_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'refuel_password')
    
    # Construct database URL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/bot.log')
    
    # Bot Settings
    MAX_RECENT_ENTRIES = int(os.getenv('MAX_RECENT_ENTRIES', '10'))
    
    @classmethod
    def validate(cls):
        """Validate that all required settings are present."""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        if not cls.DB_PASSWORD:
            raise ValueError("DB_PASSWORD is required")
        return True

# Create settings instance
settings = Settings()
