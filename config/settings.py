import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    LOG_LEVEL: str = Field(default="INFO")
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./amfi.db")
    AMFI_NAV_URL: str = Field(default="https://www.amfiindia.com/spages/NAVAll.txt")
    SCRAPER_TIMEOUT: int = Field(default=30)
    SCRAPER_RETRY_COUNT: int = Field(default=3)
    SCRAPER_RETRY_DELAY: int = Field(default=5)
    SCHEDULER_CRON_HOUR: int = Field(default=23)
    SCHEDULER_CRON_MINUTE: int = Field(default=0)
    NOTIFICATION_CHANNEL: str = Field(default="console")

    # SMTP Settings
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    SMTP_TO: str = Field(default="")

    # Slack Settings
    SLACK_WEBHOOK_URL: str = Field(default="")

    # Telegram Settings
    TELEGRAM_BOT_TOKEN: str = Field(default="")
    TELEGRAM_CHAT_ID: str = Field(default="")

    # Look for .env file at the project root or current working dir
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings globally
settings = Settings()
