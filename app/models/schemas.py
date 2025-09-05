from pydantic import BaseModel, Field
from typing import Optional, Union, List, Dict, Any
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str 
    up_time: Optional[float] = None 

class ModelInfo(BaseModel):
    model_type: Optional[str] = None
    prediction_timestamp: Optional[str] = None

class PredictionRequest(BaseModel):
    text: Union[str, List[str]] = Field(
        ..., 
        description = "Input text for predictions"
    )

class PredictionResponse(BaseModel):
    success: bool
    prediction: Union[List[float], float, int, str]
    confidence: Optional[float] = None 
    prediction_probabilites: Optional[List[List[float]]] = None
    from_cache: bool
    cache_key: Optional[str] = None 
    processing_time_seconds: float 
    model_info: ModelInfo
    metadata: Optional[Dict[str, Any]] = None 

class CacheInfoResponse(BaseModel):
    success: bool
    exists: bool
    cache_key: str
    message: str = None
    ttl_seconds: Optional[int] = None
    prediction_timestamp: Optional[str] = None
    model_type: Optional[str] = None
    has_probabilities: bool = False
    prediction_summary: Optional[Dict[str, Any]] = None

class CacheStatus(BaseModel):
    status: str
    redis_version: Optional[str] = None
    connected_clients: Optional[int] = None
    used_memory_human: Optional[str] = None
    keyspace_hits: Optional[int] = None
    keyspace_misses: Optional[int] = None
    error: Optional[str] = None

class ModelStatus(BaseModel):
    status: str
    model_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CacheStatsResponse(BaseModel):
    success: bool
    service_status: str
    cache_status: CacheStatus
    model_status: ModelStatus
    timestamp: float