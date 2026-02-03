from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://analyzer:analyzer_pass@localhost:5432/marketplace_analyzer"
    
    # Celery
    CELERY_BROKER_URL: str = "amqp://analyzer:analyzer_pass@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # S3/MinIO
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "analyzer"
    S3_SECRET_KEY: str = "analyzer_pass"
    S3_BUCKET: str = "marketplace-images"
    S3_REGION: str = "us-east-1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    EBAY_APP_ID: Optional[str] = None
    EBAY_CERT_ID: Optional[str] = None
    EBAY_DEV_ID: Optional[str] = None
    AMAZON_ACCESS_KEY: Optional[str] = None
    AMAZON_SECRET_KEY: Optional[str] = None
    STOCKX_API_KEY: Optional[str] = None
    GRAILED_API_KEY: Optional[str] = None
    
    # ML Models
    MODEL_TYPE: str = "yolov8"
    MODEL_PATH: str = "models/yolov8n.pt"
    MODEL_CONF_THRESHOLD: float = 0.25
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
