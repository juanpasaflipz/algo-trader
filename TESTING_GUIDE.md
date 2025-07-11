# Testing Guide for Phase 0 Refactoring

This guide helps you test all the new features implemented in Phase 0 of the refactoring.

## Prerequisites

1. **Virtual Environment**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Environment Variables**
   Make sure `.env` file exists with:
   ```
   DATABASE_URL=postgresql+asyncpg://localhost/algo_trader
   TRADINGVIEW_WEBHOOK_SECRET=your-webhook-secret
   SECRET_KEY=your-secret-key-change-in-production
   ```

3. **Redis** (for Celery)
   - macOS: `brew services start redis`
   - Linux: `sudo service redis-server start`
   - Windows: Use WSL or Docker

## Quick Test Options

### Option 1: Local Testing (Recommended for Development)

1. **Start Redis** (if not using Docker)
   ```bash
   redis-server
   ```

2. **Start Celery Worker** (new terminal)
   ```bash
   source venv/bin/activate
   celery -A celery_worker worker --loglevel=info
   ```

3. **Start Celery Beat** (new terminal, optional)
   ```bash
   source venv/bin/activate
   celery -A celery_worker beat --loglevel=info
   ```

4. **Start Flower** (new terminal, optional)
   ```bash
   source venv/bin/activate
   celery -A celery_worker flower --port=5555
   ```

5. **Start API Server** (new terminal)
   ```bash
   source venv/bin/activate
   python main.py
   ```

6. **Run Test Script**
   ```bash
   python scripts/test_refactoring.py
   ```

### Option 2: Docker Testing (Easier Setup)

```bash
# Start all services
./test_with_docker.sh

# Or manually:
docker-compose up -d

# Run tests
python scripts/test_refactoring.py

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Manual Testing

### 1. New API Endpoints (Phase 0.1)

**Authentication Endpoints:**
```bash
# Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass", "full_name": "Test User"}'

# Login (get token)
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass"
```

**Risk Profiling:**
```bash
# Submit risk assessment
curl -X POST http://localhost:8000/api/v1/profile/risk-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "responses": [
      {"question_id": "q1", "answer": "moderate", "score": 5},
      {"question_id": "q2", "answer": "long-term", "score": 7}
    ]
  }'

# Get strategy recommendations
curl http://localhost:8000/api/v1/profile/strategy-recommendations
```

### 2. Async Tasks (Phase 0.2)

**Create Async Backtest:**
```bash
# Start a backtest task
curl -X POST http://localhost:8000/api/v1/tasks/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "EMA_CROSSOVER",
    "symbol": "BTCUSDT",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "initial_capital": 10000
  }'

# Check task status (replace TASK_ID)
curl http://localhost:8000/api/v1/tasks/TASK_ID
```

**Async Webhook Processing:**
```bash
# Process webhook asynchronously
curl -X POST "http://localhost:8000/api/v1/webhook/tradingview?async_processing=true" \
  -H "Authorization: Bearer your-webhook-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "EMA_Crossover",
    "symbol": "BTCUSDT",
    "signal": "buy",
    "price": 50000
  }'
```

### 3. Telemetry & Metrics (Phase 0.3)

**View Metrics:**
- Prometheus format: http://localhost:8000/metrics
- Flower UI: http://localhost:5555
- API Docs: http://localhost:8000/docs

**Check Request Headers:**
```bash
# Look for X-Request-ID and X-Process-Time headers
curl -i http://localhost:8000/api/v1/health
```

**Generate Metrics:**
```bash
# Run telemetry example
python scripts/telemetry_example.py
```

## Monitoring URLs

| Service | URL | Purpose |
|---------|-----|---------|
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Flower | http://localhost:5555 | Celery task monitoring |
| Prometheus | http://localhost:9090 | Metrics (if using docker-compose) |
| Metrics | http://localhost:8000/metrics | Raw Prometheus metrics |

## Troubleshooting

### Import Errors
```bash
# Verify imports work
python test_minimal_startup.py
```

### Celery Not Working
1. Check Redis is running: `redis-cli ping`
2. Check Celery worker logs
3. Verify broker URL in `.env`

### API Not Starting
1. Check port 8000 is free: `lsof -i :8000`
2. Check environment variables
3. Review error logs

### Docker Issues
1. Ensure Docker is running
2. Check logs: `docker-compose logs app`
3. Rebuild if needed: `docker-compose build --no-cache`

## What's Been Tested

✅ **Phase 0.1**: Directory restructuring
- New API structure with renamed endpoints
- Auth and profiling endpoints
- Backward compatibility

✅ **Phase 0.2**: Task Queue
- Celery worker processing
- Async task creation and monitoring
- Task progress tracking
- Flower UI integration

✅ **Phase 0.3**: Telemetry
- Structured logging with structlog
- Prometheus metrics collection
- Request tracking with X-Request-ID
- Performance timing middleware

## Next Steps

After testing Phase 0:
1. Review logs for any errors
2. Check metrics to ensure they're being collected
3. Verify all endpoints are accessible
4. Proceed to Phase 1 (Authentication implementation)