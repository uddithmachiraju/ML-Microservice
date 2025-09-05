import time 
from fastapi import APIRouter, Query, HTTPException
from app.services.ml_service import ml_service
from app.models.schemas import (
    PredictionRequest, PredictionResponse, 
    CacheStatsResponse, CacheInfoResponse
)
from app.services.prediction_service import prediction_service
from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger("api")

router = APIRouter()

@router.post("/predict", response_model = PredictionResponse)
async def predict(request: PredictionRequest, use_cache: bool = Query(True, description = "Whether to use caching")) -> PredictionResponse:
    """Make a prediction"""
    start_time = time.time()

    try:
        result = await prediction_service.predict_single(
            text = request.text, 
            use_cache = use_cache
        )

        processing_time = time.time() - start_time

        return PredictionResponse(
            success = True, 
            prediction = result["prediction"], 
            confidence = result.get("confidence"), 
            prediction_probabilites = result.get("prediction_probabilities"), 
            from_cache = result["from_cache"], 
            cache_key = result.get("cache_key"), 
            processing_time_seconds = processing_time, 
            model_info = result.get("model_info", {}), 
            metadata = {
                "input size": result.get("input size"), 
                "cached": result.get("cached", False)
            }
        )
    except Exception as e:
        logger.error(f"Prediction endpoint error: {str(e)}")
        raise HTTPException(status_code = 500, detail = str(e)) 
    
@router.get("/model/info")
async def get_model_info():
    """Get information about the model"""
    try:
        model_info = ml_service.get_model_info()

        return {
            "success": True, 
            "model_info": model_info
        }
    except Exception as e:
        logger.error(f"Model info endpoint error {str(e)}")
        raise HTTPException(status_code = 500, detail = str(e)) 

@router.get("/cache/stats", response_model = CacheStatsResponse)
async def get_cache_stats():
    """Get cache and model statistics"""
    try:
        result = await prediction_service.get_cache_stats()

        return CacheStatsResponse(
            success = True, 
            service_status = result["service_status"], 
            cache_status = result["cache_status"], 
            model_status = result["model_status"], 
            timestamp = time.time() 
        )
    except Exception as e:
        logger.error(f"Cache status endpoint error: {str(e)}")
        raise HTTPException(status_code = 500, detail = str(e)) 
    
@router.get("/cache/info", response_model = CacheInfoResponse)
async def get_cache_info(cache_key: str) ->CacheInfoResponse:
    """Get information about a cached prediction"""
    try:
        result = await prediction_service.get_prediction_info(cache_key)

        return CacheInfoResponse(
            success = True, 
            exists = result["exists"], 
            cache_key = cache_key, 
            message = result.get("message", ""),
            ttl_seconds = result.get("ttl_seconds", ""), 
            prediction_timestamp = result.get("prediction_timestamp", ""), 
            model_type = result.get("model_type", ""), 
            has_probabilities = result.get("has_probabilities", False), 
            prediction_summary = result.get("prediction_summary", ""), 
        )
    except Exception as e:
        logger.error(f"Cache info endpoint error: {str(e)}")
        raise HTTPException(status_code = 500, detail = str(e)) 
    
@router.delete("/cache")
async def flush_cache():
    """Flush all cached predictions"""
    pass 