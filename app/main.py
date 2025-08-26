from fastapi import FastAPI, Request
import uvicorn 
import time 
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.api.routes import health
from app.core.exceptions import CustomException

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

    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next): 
        start_time = time.time() 
        response = await call_next(request)
        process_time = time.time() - start_time 
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Request {request.method} {request.url} - {response.status_code} - {process_time:.4f}s")
        return response 
    
    # Custom Exception Handler
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            content = {
                "error": exc.message, 
                "details": exc.details
            }
        )
    
    # Exception Handler
    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandler Exception: {str(exc)}")
        return JSONResponse(
            status_code = 500, 
            content = {
                "error" : "Internal server error"
            }
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