from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str 
    up_time: Optional[float] = None 