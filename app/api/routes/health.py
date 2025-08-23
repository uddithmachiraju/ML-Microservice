from fastapi import APIRouter
import time 
from datetime import datetime 
from app.core.config import settings
from app.core.logging import setup_logging, LoggerMixin

router = APIRouter()

startup_time = time.time()

class Health(LoggerMixin):
    async def health(self):
        self.logger.info(f"health endpoint is called")
        return {
            "status": "healthy", 
            "timestamp": datetime.now(),
            "version": settings.app_version, 
            "up_time": time.time() - startup_time
        }

health_class = Health()

@router.get("/health")
async def health():
    return await health_class.health() 