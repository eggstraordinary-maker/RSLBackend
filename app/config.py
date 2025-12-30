from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str
    database_url_async: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Email
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    email_from: str

    # Frontend
    frontend_url: str = "http://localhost:5173"

    # App
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
