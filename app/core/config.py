from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    app_name: str = "MicroML"
    app_version: str = "1.0.0"
    debug: bool = True  

    # API settings
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000 

    # Logging
    logs_directory: str = "logs" 
    log_level: str = "INFO" 

    # redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_ttl: int = 3000 

    # Ml model settings
    model_path: str = "/workspace/app/models/ml_models/checkpoints/model.pkl"
    vectorizer_path: str = "/workspace/app/models/ml_models/checkpoints/vectorizer.pkl"
    model_threshold: float = 0.5

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = False 

settings = Settings() 