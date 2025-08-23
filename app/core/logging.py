import os 
import logging
import logging.config
from datetime import datetime 
from typing import Optional, Dict, Any 
from app.core.config import settings

def setup_logging(log_level: Optional[str] = None) -> None:
    level = log_level or settings.log_level

    # Ensure the logs directory exists
    os.makedirs(os.path.abspath(settings.logs_directory), exist_ok = True)

    # log filename with timestamp
    log_filename = os.path.join(
        settings.logs_directory, 
        f"microml_{datetime.now().strftime('%Y%m%d')}.log"
    )

    # Setting up logging config
    logging_config: Dict[str, Any] = {
        "version": 1, 
        "disable_existing_loggers" : False, 

        "formatters": {
            # Console logs
            "console": {
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            },
            # File logs
            "detailed": {
                "format": (
                    "%(asctime)s - %(levelname)s - %(name)s - "
                    "%(filename)s:%(lineno)d - %(funcName)s - %(message)s"
                )
            },
            # Json logs
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter", 
                "fmt": (
                    # "timestamp levelname name filename lineno funcName message"
                    "%(asctime)s %(levelname)s %(name)s %(filename)s %(lineno)d %(funcName)s %(message)s"
                ),
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            }
        },

        "handlers": {
            # Console output handler
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
                "level": "INFO",
                "stream": "ext://sys.stdout",
            },

            # Rotating file handler for general app logs (INFO and DEBUG)
            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_filename,
                "mode": "a",
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 7,
                "encoding": "utf-8",
                "formatter": "detailed",
                "level": "DEBUG" if settings.debug else "INFO",
            },

            # Rotating file handler for JSON formatted error logs
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(settings.logs_directory, "errors.json.log"),
                "mode": "a",
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 10,
                "encoding": "utf-8",
                "formatter": "json",
                "level": "ERROR",
            },
        },

        "loggers": {
            # Root logger captures logs from all libraries
            "": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
            },
            # Core FastAPI backend app
            "app": {
                "level": "DEBUG" if settings.debug else "INFO",
                "handlers": ["console", "app_file", "error_file"],
                "propagate": False,
            },
            # Services layer (Kubernetes, Redis, Docker)
            "app.services": {
                "level": "INFO",
                "handlers": ["app_file", "error_file"],
                "propagate": False,
            },
            # API endpoints layer
            "app.api": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
                "propagate": False,
            },
            # External libraries can stay default but you may tune as needed
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "app_file", "error_file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console", "app_file"],
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"app.{name}") 

class LoggerMixin:
    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__name__) 