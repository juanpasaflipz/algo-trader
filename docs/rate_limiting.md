# Rate Limiting Documentation

## Overview

The Algo Trader platform implements comprehensive rate limiting to protect against API abuse, manage resource consumption, and ensure fair usage across all clients.

## Implementation

Rate limiting is implemented using `slowapi`, a FastAPI-compatible rate limiting library that supports:
- Redis-backed distributed rate limiting
- Per-endpoint custom limits
- API key and IP-based limiting
- Adaptive rate limiting based on user behavior

## Rate Limits by Endpoint Type

### Critical Endpoints

| Endpoint | Rate Limit | Purpose |
|----------|------------|---------|
| `/webhook/tradingview` | 10/min, 100/hour | Prevent webhook spam |
| `/ai/*` | 20/min, 200/hour | Control expensive AI API usage |
| `/trading/emergency-stop` | 5/min | Allow emergency use but prevent abuse |

### Trading Operations

| Endpoint | Rate Limit | Purpose |
|----------|------------|---------|
| `/trading/control` | 30/min, 500/hour | Strategy management |
| `/backtest` | 10/min, 50/hour | Resource-intensive operations |

### Monitoring & Status

| Endpoint | Rate Limit | Purpose |
|----------|------------|---------|
| `/trading/status` | 60/min, 1000/hour | Allow frequent monitoring |
| `/metrics` | 100/min | Prometheus metrics |

### Authentication

| Endpoint | Rate Limit | Purpose |
|----------|------------|---------|
| `/auth/login` | 5/min, 20/hour | Prevent brute force |
| `/auth/register` | 3/min, 10/hour | Prevent spam accounts |

## Rate Limit Headers

All responses include rate limit headers:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1609459200
Retry-After: 60
```

## Rate Limit Key Priority

1. **API Key** (header: `X-API-Key` or query param: `api_key`)
2. **IP Address** (fallback if no API key)

## Special IP Allowlists

TradingView webhook IPs receive higher limits:
- 52.89.214.238
- 34.212.75.30
- 54.218.53.128
- 52.32.178.7

Rate limit: 100/min, 5000/hour

## Configuration

### Environment Variables

```bash
# Redis URL for distributed rate limiting
REDIS_URL=redis://localhost:6379

# Enable/disable rate limiting
RATE_LIMIT_ENABLED=true
```

### Custom Rate Limits

Create custom rate limits in your endpoints:

```python
from app.core.rate_limit import create_rate_limit

@router.get("/custom-endpoint")
@create_rate_limit("5 per second, 100 per minute")
async def custom_endpoint(request: Request):
    return {"status": "ok"}
```

## Adaptive Rate Limiting

The system tracks user behavior and adjusts limits:
- **Good standing users**: 2x base limit
- **Repeat violators**: Reduced limits (10 requests less per violation)
- **Minimum limit**: 10 requests/minute

## Error Responses

Rate limit exceeded returns HTTP 429:

```json
{
    "detail": "Rate limit exceeded",
    "limit": "10 per 1 minute",
    "error": "rate_limit_exceeded"
}
```

## Testing Rate Limits

```bash
# Test webhook rate limit
for i in {1..15}; do
    curl -X POST http://localhost:8000/api/v1/webhook/tradingview \
         -H "X-API-Key: test_key" \
         -H "Content-Type: application/json" \
         -d '{"strategy":"test","symbol":"BTCUSDT","signal":"buy","price":50000}'
    sleep 1
done
```

## Monitoring

Rate limit violations are tracked in Prometheus metrics:

```
rate_limit_violations_total{endpoint="/api/v1/webhook/tradingview", method="POST"} 5
```

## Best Practices

1. **Use API Keys**: Register for higher limits and better tracking
2. **Implement Backoff**: Respect `Retry-After` header
3. **Batch Requests**: Combine multiple operations when possible
4. **Monitor Usage**: Track your rate limit headers
5. **Cache Responses**: Reduce unnecessary API calls

## Troubleshooting

### "Rate limit exceeded" errors

1. Check rate limit headers in previous responses
2. Implement exponential backoff
3. Request API key for higher limits
4. Consider upgrading to partner tier

### Redis Connection Issues

If Redis is unavailable, rate limiting falls back to in-memory storage (per-instance limits).

```bash
# Check Redis connection
redis-cli ping
```

### Debug Rate Limiting

Enable debug logging:

```python
# In app/core/config.py
LOG_LEVEL=DEBUG
```

View rate limit keys in Redis:

```bash
redis-cli keys "slowapi:*"
```