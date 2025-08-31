import redis
import json 
import pickle
from typing import Optional, Any

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
        
    def get(self, key: str) -> Optional[Any]:
        """Retrive value from cache"""
        try:
            value = self.client.get(key)
            if value is None:
                logger.debug(f"Cache miss for the key: {key}")
                return None 

            try:
                result = json.loads(value.decode("utf-8"))
                logger.debug(f"Cache hit for key: {key}")
                return result
            except (json.JSONDecodeError, UnicodeDecodeError):
                result = pickle.loads(value)
                logger.debug(f"Cache hit for key: {key}")
                return result
        
        except redis.RedisError as e:
            logger.error(f"Redis get error for the {key}: {str(e)}") 
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """stores value in cache"""
        try:
            try:
                serialized_value = json.dumps(value, default = str)
            except (TypeError, ValueError):
                serialized_value = pickle.dumps(value)

            ttl = ttl or settings.redis_ttl
            result = self.client.setex(key, ttl, serialized_value)

            if result:
                logger.debug(f"Cached value for the key: {key} (TTL): {ttl}s")
            return result
        
        except redis.RedisError as e:
            logger.error(f"Redis set error for the key: {str(e)}")
            return False 
        
    def delete(self, key: str) -> bool:
        """Deletes key from cache"""
        try:
            result = self.client.delete(key)
            logger.debug(f"Deleted key from cache: {key}")
            return bool(result)
        except redis.RedisError as e:
            logger.error(f"Redis delete error for key {key}: {str(e)}")
            return False
        
    def exists(self, key: str) -> bool:
        """Chechk if key exists in cache"""
        try:
            result = self.client.exists(key)
            return bool(result)
        except redis.RedisError as e:
            logger.error(f"Redis exists error for key {key}: {str(e)}")
            return False
        
    def get_ttl(self, key: str) -> int:
        """Get remaining TTL for the key"""
        try:
            return self.client.ttl(key)
        except redis.RedisError as e:
            logger.error(f"Redis exists error for key {key}: {str(e)}") 
            return False
        
    def flush_all(self) -> bool:
        """Clear all cache"""
        try:
            self.client.flushdb()
            logger.warning("Flushed all cache data")
            return True 
        except redis.RedisError as e:
            logger.error(f"Redis flush error: {str(e)}")
            return False
        
    def health_check(self) -> dict:
        try:
            info = self.client.info()
            return {
                "status": "healthy", 
                "redis_version": info.get("redis_version"), 
                "connected_clients": info.get("connected_clients"), 
                "used_memory_human": info.get("used_memory_human"), 
                "keyspace_hits": info.get("keyspace_hits", 0), 
                "keyspace_misses": info.get("keyspace_misses", 0) 
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e)
            }
        
cache_service = CacheService() 