from fastapi import FastAPI
import uvicorn 
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.api.routes import health

# Setup logging 
logger = get_logger("api") 

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging() 
    # Startup logic
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    yield
    # Shutdown logic
    logger.info("Shutting down application")

def create_application() -> FastAPI:
    # Create application
    app = FastAPI(
        title = settings.app_name, 
        version = settings.app_version, 
        debug = settings.debug, 
        docs_url = "/docs" if settings.debug else None,
        lifespan = lifespan
    )
    
    # Include routers
    app.include_router(health.router, prefix = settings.api_prefix, tags = ["health"])

    return app 

app = create_application() 

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host = settings.host, 
        port = settings.port, 
        reload = settings.debug, 
        log_config = None, 
        log_level = None
    )