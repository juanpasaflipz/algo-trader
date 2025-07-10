from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from app.core.config import settings
from app.core.logger import logger
from app.api.v1 import tradingview_webhook, backtest, trade_controller, status, ai_analysis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Algo Trader", version=settings.app_version)
    
    # TODO: Initialize database connection
    # TODO: Initialize Redis connection
    # TODO: Start background tasks
    
    yield
    
    # Shutdown
    logger.info("Shutting down Algo Trader")
    # TODO: Close database connections
    # TODO: Close Redis connections
    # TODO: Cancel background tasks


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics endpoint
if settings.enable_metrics:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

# Include API routes
app.include_router(
    status.router,
    prefix=settings.api_v1_prefix,
    tags=["status"]
)

app.include_router(
    tradingview_webhook.router,
    prefix=settings.api_v1_prefix,
    tags=["webhooks"]
)

app.include_router(
    backtest.router,
    prefix=settings.api_v1_prefix,
    tags=["backtest"]
)

app.include_router(
    trade_controller.router,
    prefix=settings.api_v1_prefix,
    tags=["trading"]
)

app.include_router(
    ai_analysis.router,
    prefix=settings.api_v1_prefix,
    tags=["ai"]
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        path=request.url.path,
        method=request.method
    )
    return {"detail": "Internal server error"}, 500


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )