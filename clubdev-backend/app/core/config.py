import json

from pydantic.v1 import BaseSettings
import secrets
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 1800
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    google_auth_url: str
    google_token_url: str
    google_userinfo_url: str
    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str
    github_auth_url: str
    github_token_url: str
    github_userinfo_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region_name: str
    aws_bucket_name: str
    stripe_secret_key: str
    stripe_public_key: str
    genai_api_key: str
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()


with open('/Volumes/BryanAntoineHD/repos/theclubdevapp/clubdev-backend/thresholds.json', 'r') as f:
    thresholds = json.load(f)