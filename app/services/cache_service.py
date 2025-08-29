import redis
from app.core.config import settings
from app.core.exceptions import CustomException
from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger("cache_service") 

class CacheService:
    """Redis cache service for storing and retrieving predictions"""
    def __init__(self):
        self.client = None 
        self._connect()

    def _connect(self):
        """Establish a connection with redis"""
        try:
            self.client = redis.Redis(
                host = settings.redis_host, 
                port = settings.redis_port, 
                db = settings.redis_db, 
                password = settings.redis_password, 
                decode_responses = False, 
                socket_connect_timeout = 5, 
                socket_timeout = 5, 
                retry_on_timeout = True, 
                health_check_interval = 30
            )
            self.client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise CustomException(
                message = "Cache Service unavailable", 
                status_code = 503, 
                details = "Redis Connection Failed"
            )