"""
Rate limiting implementation for the Algo Trader API.
Protects endpoints from abuse and manages resource consumption.
"""

from typing import Callable, Optional
from functools import wraps
import redis.asyncio as redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.telemetry import get_logger, metrics

logger = get_logger(__name__)


# Custom key function that can use API keys or IP addresses
async def get_rate_limit_key(request: Request) -> str:
    """
    Generate rate limit key based on API key or IP address.
    Priority: API Key > IP Address
    """
    # Check for API key in headers
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"
    
    # Check for API key in query params (webhook compatibility)
    api_key = request.query_params.get("api_key")
    if api_key:
        return f"api_key:{api_key}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Create Redis-backed storage if Redis is configured
storage_uri = None
if settings.redis_url:
    storage_uri = settings.redis_url


# Initialize the limiter with Redis backend for distributed rate limiting
limiter = Limiter(
    key_func=get_rate_limit_key,
    storage_uri=storage_uri,
    default_limits=["1000 per hour"],  # Global default limit
    headers_enabled=True,  # Add rate limit headers to responses
)


# Custom rate limit exceeded handler
def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom handler for rate limit exceeded errors."""
    response = JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
            "limit": exc.limit,
            "error": "rate_limit_exceeded"
        }
    )
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(exc.limit.amount)
    response.headers["X-RateLimit-Remaining"] = "0"
    response.headers["X-RateLimit-Reset"] = str(exc.limit.reset_at)
    response.headers["Retry-After"] = str(exc.retry_after)
    
    # Log rate limit violation
    logger.warning(
        "Rate limit exceeded",
        limit=str(exc.limit),
        key=get_rate_limit_key(request),
        path=request.url.path
    )
    
    # Update metrics
    metrics.rate_limit_violations.labels(
        endpoint=request.url.path,
        method=request.method
    ).inc()
    
    return response


# Predefined rate limit decorators for different endpoint types
class RateLimits:
    """Common rate limit configurations for different endpoint types."""
    
    # Critical endpoints - very restrictive
    WEBHOOK = limiter.limit("10 per minute, 100 per hour")
    AI_ANALYSIS = limiter.limit("20 per minute, 200 per hour")  # AI API is expensive
    EMERGENCY_STOP = limiter.limit("5 per minute")  # Prevent spam but allow emergency use
    
    # Trading operations - moderate limits
    TRADING_CONTROL = limiter.limit("30 per minute, 500 per hour")
    BACKTEST = limiter.limit("10 per minute, 50 per hour")  # Backtests are resource-intensive
    
    # Status and monitoring - more permissive
    STATUS = limiter.limit("60 per minute, 1000 per hour")
    MONITORING = limiter.limit("100 per minute")
    
    # Authentication endpoints
    AUTH_LOGIN = limiter.limit("5 per minute, 20 per hour")  # Prevent brute force
    AUTH_REGISTER = limiter.limit("3 per minute, 10 per hour")
    
    # General API endpoints
    DEFAULT = limiter.limit("100 per minute, 1000 per hour")


def apply_rate_limiting(app):
    """Apply rate limiting middleware to FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)
    
    logger.info(
        "Rate limiting configured",
        storage_backend="redis" if storage_uri else "memory",
        redis_url=storage_uri if storage_uri else "in-memory"
    )


# Utility function to create custom rate limits
def create_rate_limit(limit_string: str) -> Callable:
    """
    Create a custom rate limit decorator.
    
    Args:
        limit_string: Rate limit string (e.g., "10 per minute", "100 per hour")
    
    Returns:
        Rate limit decorator
    """
    return limiter.limit(limit_string)


# IP-based rate limiting for specific IPs (e.g., known partners)
class IPRateLimits:
    """Special rate limits for specific IP addresses or partners."""
    
    # Partner webhook IPs get higher limits
    PARTNER_LIMITS = {
        # TradingView IPs (example - replace with actual IPs)
        "52.89.214.238": "100 per minute, 5000 per hour",
        "34.212.75.30": "100 per minute, 5000 per hour",
        "54.218.53.128": "100 per minute, 5000 per hour",
        "52.32.178.7": "100 per minute, 5000 per hour",
    }
    
    @staticmethod
    def get_limit_for_ip(ip: str) -> Optional[str]:
        """Get custom rate limit for specific IP."""
        return IPRateLimits.PARTNER_LIMITS.get(ip)


# Adaptive rate limiting based on user behavior
class AdaptiveRateLimiter:
    """
    Adaptive rate limiting that adjusts based on user behavior.
    Good clients get higher limits, suspicious ones get throttled.
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.base_limit = 100  # Base requests per minute
        
    async def get_adaptive_limit(self, key: str) -> int:
        """Calculate adaptive limit based on user history."""
        if not self.redis:
            return self.base_limit
            
        # Check user's violation history
        violations_key = f"rate_violations:{key}"
        violations = await self.redis.get(violations_key)
        
        if violations:
            violation_count = int(violations)
            # Reduce limit for repeat offenders
            return max(10, self.base_limit - (violation_count * 10))
        
        # Check if user is authenticated and has good standing
        good_standing_key = f"good_standing:{key}"
        if await self.redis.get(good_standing_key):
            # Increase limit for users in good standing
            return self.base_limit * 2
            
        return self.base_limit
    
    async def record_violation(self, key: str):
        """Record a rate limit violation."""
        if not self.redis:
            return
            
        violations_key = f"rate_violations:{key}"
        await self.redis.incr(violations_key)
        await self.redis.expire(violations_key, 3600)  # Reset after 1 hour


# Export rate limit exceeded exception for use in tests
__all__ = [
    "limiter",
    "RateLimits",
    "apply_rate_limiting",
    "create_rate_limit",
    "RateLimitExceeded",
    "AdaptiveRateLimiter",
    "IPRateLimits"
]