"""Middleware for request tracking and telemetry."""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.telemetry import get_logger, metrics, set_request_id, clear_request_id

logger = get_logger(__name__)


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Middleware to track requests and collect metrics."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        set_request_id(request_id)
        
        # Start timing
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Update metrics
            metrics.http_requests.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            metrics.http_request_duration.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            # Log response
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_seconds=duration,
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Update error metrics
            metrics.http_requests.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
            
            metrics.error_rate.labels(
                error_type=type(e).__name__,
                component="http_middleware"
            ).inc()
            
            # Log error
            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_seconds=duration,
                exc_info=True
            )
            
            raise
            
        finally:
            # Clear request context
            clear_request_id()


class TimingRoute(APIRoute):
    """Custom route class that adds timing information to responses."""
    
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request) -> Response:
            start_time = time.time()
            response = await original_route_handler(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            return response
        
        return custom_route_handler