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

    class Config:
        env_file = ".env"
        extra = "ignore"
        case_sensitive = False 

settings = Settings() 