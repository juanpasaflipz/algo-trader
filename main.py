from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from app.core.config import settings
from app.core.telemetry import get_logger, metrics, configure_logging
from app.core.middleware import TelemetryMiddleware, TimingRoute
from app.core.rate_limit import apply_rate_limiting
from app.api.v1 import (
    webhooks,  # renamed from tradingview_webhook
    strategies,  # renamed from backtest
    execution,  # renamed from trade_controller
    status,
    ai_analysis,
    auth,  # new
    profiling,  # new
    tasks,  # new - async task management
)


logger = get_logger(__name__)

# Configure telemetry based on environment
configure_logging(
    log_level=settings.log_level,
    log_format="json" if settings.is_production else "console"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Algo Trader", version=settings.app_version)
    
    # Set system health metrics
    metrics.system_health.labels(component="api").set(1)

    # TODO: Initialize database connection
    # TODO: Initialize Redis connection
    # TODO: Start background tasks

    yield

    # Shutdown
    logger.info("Shutting down Algo Trader")
    metrics.system_health.labels(component="api").set(0)
    # TODO: Close database connections
    # TODO: Close Redis connections
    # TODO: Cancel background tasks


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Apply rate limiting
apply_rate_limiting(app)

# Add telemetry middleware
app.add_middleware(TelemetryMiddleware)

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
app.include_router(status.router, prefix=settings.api_v1_prefix, tags=["status"])

app.include_router(
    auth.router, prefix=settings.api_v1_prefix, tags=["auth"]
)

app.include_router(
    profiling.router, prefix=settings.api_v1_prefix, tags=["profiling"]
)

app.include_router(
    webhooks.router, prefix=settings.api_v1_prefix, tags=["webhooks"]
)

app.include_router(strategies.router, prefix=settings.api_v1_prefix, tags=["strategies"])

app.include_router(
    execution.router, prefix=settings.api_v1_prefix, tags=["execution"]
)

app.include_router(ai_analysis.router, prefix=settings.api_v1_prefix, tags=["ai"])

app.include_router(tasks.router, prefix=settings.api_v1_prefix, tags=["tasks"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        path=request.url.path,
        method=request.method,
    )
    return {"detail": "Internal server error"}, 500


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
