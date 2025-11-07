import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_HOST: str = '0.0.0.0'
    APP_PORT: int = 8000
    # LLM
    LLM_API_URL: str = os.getenv('LLM_API_URL', 'https://api.groq.com/openai/v1/chat/completions')
    LLM_API_KEY: str = os.getenv('LLM_API_KEY', '')
    # Email / Twilio
    SMTP_HOST: str = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER: str = os.getenv('SMTP_USER', '')
    SMTP_PASS: str = os.getenv('SMTP_PASS', '')
    # Data sources
    PROPERTIES_CSV: str = os.getenv('PROPERTIES_CSV', '/data/properties.csv')
    MYSQL_URL: str = os.getenv('MYSQL_URL', '')
    # Redis
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    TWILIO_SID: str = os.getenv('TWILIO_SID', '')
    TWILIO_TOKEN: str = os.getenv('TWILIO_TOKEN', '')
    TWILIO_FROM: str = os.getenv('TWILIO_FROM', '')
    
class Config:
    env_file = '.env'

settings = Settings()