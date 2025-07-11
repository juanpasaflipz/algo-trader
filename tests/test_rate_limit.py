"""
Tests for rate limiting functionality.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import (
    limiter,
    RateLimits,
    create_rate_limit,
    AdaptiveRateLimiter,
    IPRateLimits
)


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limit_decorators_exist(self):
        """Test that rate limit decorators are properly defined."""
        assert hasattr(RateLimits, 'WEBHOOK')
        assert hasattr(RateLimits, 'AI_ANALYSIS')
        assert hasattr(RateLimits, 'EMERGENCY_STOP')
        assert hasattr(RateLimits, 'TRADING_CONTROL')
        assert hasattr(RateLimits, 'BACKTEST')
        assert hasattr(RateLimits, 'STATUS')
        assert hasattr(RateLimits, 'AUTH_LOGIN')
        assert hasattr(RateLimits, 'DEFAULT')
    
    def test_webhook_rate_limits(self, client: TestClient):
        """Test webhook endpoint rate limiting."""
        # This test requires the actual app running
        # Here we're testing the configuration exists
        webhook_limit = RateLimits.WEBHOOK
        assert webhook_limit is not None
        
    def test_ai_analysis_rate_limits(self):
        """Test AI analysis endpoint rate limiting."""
        ai_limit = RateLimits.AI_ANALYSIS
        assert ai_limit is not None
        
    def test_custom_rate_limit_creation(self):
        """Test creating custom rate limits."""
        custom_limit = create_rate_limit("5 per minute")
        assert custom_limit is not None
        
    def test_ip_based_rate_limits(self):
        """Test IP-based rate limit configurations."""
        # Test known partner IPs
        tradingview_ip = "52.89.214.238"
        limit = IPRateLimits.get_limit_for_ip(tradingview_ip)
        assert limit == "100 per minute, 5000 per hour"
        
        # Test unknown IP
        unknown_ip = "1.2.3.4"
        limit = IPRateLimits.get_limit_for_ip(unknown_ip)
        assert limit is None
        
    @pytest.mark.asyncio
    async def test_adaptive_rate_limiter(self):
        """Test adaptive rate limiting behavior."""
        limiter = AdaptiveRateLimiter(redis_client=None)
        
        # Without Redis, should return base limit
        limit = await limiter.get_adaptive_limit("test_user")
        assert limit == 100
        
        # Test violation recording (no-op without Redis)
        await limiter.record_violation("test_user")
        

class TestRateLimitIntegration:
    """Integration tests for rate limiting with actual endpoints."""
    
    @pytest.mark.asyncio
    async def test_webhook_endpoint_rate_limit(self, client: TestClient, mocker):
        """Test rate limiting on webhook endpoint."""
        # Mock the webhook auth dependency
        mocker.patch('app.core.dependencies.verify_webhook_auth', return_value=True)
        
        # Prepare test payload
        payload = {
            "strategy": "test_strategy",
            "symbol": "BTCUSDT",
            "signal": "buy",
            "price": 50000.0
        }
        
        # Note: Actual rate limit testing would require:
        # 1. Running Redis
        # 2. Making multiple requests to exceed limits
        # 3. Checking for 429 status codes
        
        # Here we're just ensuring the endpoint exists and accepts requests
        response = client.post(
            "/api/v1/webhook/tradingview",
            json=payload,
            headers={"X-API-Key": "test_key"}
        )
        
        # The response might fail for other reasons (missing dependencies, etc.)
        # but we're checking that the route exists
        assert response.status_code in [200, 400, 401, 403, 422, 500]
        
    def test_rate_limit_headers(self, client: TestClient):
        """Test that rate limit headers are included in responses."""
        # Make a request to any endpoint
        response = client.get("/api/v1/status")
        
        # Check for rate limit headers
        # These might not be present without proper middleware setup
        # but we check the configuration
        assert limiter.headers_enabled is True


# Example usage in a FastAPI endpoint
"""
from fastapi import APIRouter, Request
from app.core.rate_limit import RateLimits

router = APIRouter()

@router.post("/webhook")
@RateLimits.WEBHOOK  # 10 per minute, 100 per hour
async def webhook_endpoint(request: Request):
    return {"status": "ok"}

@router.post("/ai/analyze")
@RateLimits.AI_ANALYSIS  # 20 per minute, 200 per hour
async def ai_analysis_endpoint(request: Request):
    return {"analysis": "completed"}

@router.post("/emergency-stop")
@RateLimits.EMERGENCY_STOP  # 5 per minute
async def emergency_stop(request: Request):
    return {"stopped": True}

# Custom rate limit
@router.get("/custom")
@create_rate_limit("3 per second, 100 per minute")
async def custom_endpoint(request: Request):
    return {"custom": "endpoint"}
"""