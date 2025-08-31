from typing import Union, List, Dict, Any 
import hashlib
import json

from app.services.cache_service import cache_service
from app.services.ml_service import ml_service
from app.core.logging import setup_logging, get_logger 
from app.utils.hash_utils import generate_cache_key

# Setup logging
setup_logging()
logger = get_logger("prediction_service")

class PredictionService:
    """Service that orchestrates caching and ML predictions"""

    def __init__(self):
        self.cache = cache_service
        self.ml_model = ml_service

    async def predict_single(self, features: Union[List, Dict], use_cache: bool = True) -> Dict[str, Any]:
        """Make a single prediction with cache support"""

        # Generate cache key
        cache_key = None 
        if use_cache:
            cache_key = generate_cache_key(features)
            logger.debug(f"Generated cache key: {cache_key}")

            # Check cache
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.info("Returning cache prediction")
                cached_result["from_cache"] = True 
                cached_result["cache_key"] = cache_key
                return cached_result 
            
        logger.info("Computing new predictions")
        try:
            prediction_result = self.ml_model.predict(features)
            enhance_result = {
                **prediction_result, 
                "from_cache": False, 
                "cache_key": cache_key, 
                "input_features": features if isinstance(features, dict) else None, 
                "input_size": len(features) if isinstance(features, (list, dict)) else None 
            }

            if use_cache and cache_key:
                cache_success = self.cache.set(cache_key, enhance_result)
                enhance_result["cached"] = cache_success
                if cache_success:
                    logger.info(f"Cached prediction result with key: {cache_key}")
                else:
                    logger.warning("Failed to cache prediction results")
            
            return enhance_result 
        except Exception as e:
            logger.error(F"Prediction Failed: {str(e)}") 
            raise 

    async def get_prediction_info(self, cache_key: str) -> Dict[str, Any]:
        """Get information about a cached prediction"""
        cached_result = self.cache.get(cache_key)
        if cached_result is None:
            return {
                "exists": False, 
                "cache_key": cache_key, 
                "message": "Prediction not found in cache"
            }
        
        ttl = self.cache.get_ttl(cache_key)

        return {
            "exists": True, 
            "cache_key": cache_key, 
            "ttl_seconds": ttl, 
            "prediction_timestamp": cached_result.get("model_info", {}).get("prediction_timestamp"), 
            "model_type": cached_result.get("model_info", {}).get("model_type"), 
            "has_probabilities": "prediction_probabilities" in cached_result,
            "prediction_summary": {
                "prediction": cached_result.get("prediction"),
                "confidence": cached_result.get("confidence"),
            }
        }
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and health information"""
        
        cache_health = self.cache.health_check()
        model_health = self.ml_model.health_check()
        
        return {
            "cache_status": cache_health,
            "model_status": model_health,
            "service_status": "healthy" if (
                cache_health.get("status") == "healthy" and 
                model_health.get("status") == "healthy"
            ) else "degraded"
        }