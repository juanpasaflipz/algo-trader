# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an algorithmic trading platform designed to:
- Connect to TradingView for strategy signals via webhooks
- Backtest trading strategies using historical data
- Execute trades across multiple exchanges/brokers (Binance, Interactive Brokers, Robinhood, etc.)
- Support both cryptocurrency and traditional asset trading

## Architecture Overview

The platform follows a modular architecture:

```
algo_trader/
├── app/
│   ├── api/v1/              # FastAPI routes
│   │   ├── tradingview_webhook.py  # TradingView signal receiver
│   │   ├── backtest.py             # Backtesting endpoints
│   │   └── trade_controller.py     # Strategy control
│   ├── core/                # Configuration, logging, errors
│   ├── models/              # Pydantic models for validation
│   ├── services/
│   │   ├── strategies/      # Trading strategy implementations
│   │   ├── broker_clients/  # Exchange/broker API clients
│   │   ├── backtester.py    # Backtesting engine
│   │   └── trader.py        # Trade execution logic
│   └── jobs/                # Background tasks and scheduling
```

## Development Commands

```bash
# Environment setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/
pytest tests/test_backtester.py -v  # Run specific test file
pytest -k "test_ema_crossover"      # Run tests matching pattern

# Code quality
black app/ tests/           # Format code
flake8 app/ tests/         # Lint code
mypy app/                  # Type checking

# Database migrations (when implemented)
alembic upgrade head       # Apply migrations
alembic revision --autogenerate -m "description"  # Create new migration
```

## Key Integration Points

### TradingView Integration
- Webhook endpoint: `POST /api/v1/webhook/tradingview`
- Expects Pine Script alerts in JSON format
- Validates incoming signals with API key authentication

### Exchange/Broker APIs
- **Binance**: Uses `ccxt` library for spot/futures trading
- **Interactive Brokers**: TWS API with `ib_insync` wrapper
- **Robinhood/Alpaca**: REST APIs for US stock trading
- All broker clients implement a common interface for easy swapping

### Data Storage
- **PostgreSQL**: Trade history, strategy performance, user data
- **Redis**: Real-time price caching, active positions, rate limiting
- Environment variables store all API credentials

## Development Workflow

1. **Strategy Development**:
   - Create new strategy in `app/services/strategies/`
   - Inherit from `BaseStrategy` class
   - Implement `generate_signals()` and `calculate_position_size()`

2. **Testing Progression**:
   - Unit tests for strategy logic
   - Backtest with historical data
   - Paper trade for live market validation
   - Deploy to live trading with small positions

3. **Adding New Exchange**:
   - Create client in `app/services/broker_clients/`
   - Implement `BrokerInterface` methods
   - Add exchange-specific error handling
   - Update configuration schema

## Important Patterns

### AI Integration
- Claude AI service in `app/services/ai_service.py`
- AI-enhanced strategies inherit from base strategies
- Webhook signals can be validated by AI before execution
- AI confidence thresholds control trade execution
- Fallback to non-AI strategies if AI service unavailable

### Error Handling
- All broker API calls wrapped in try/except blocks
- Custom exceptions in `app/core/errors.py`
- Automatic retry logic for transient failures
- Circuit breaker pattern for exchange outages
- AI failures don't block trading if configured

### Position Management
- Never exceed configured risk per trade (default 2%)
- Always set stop-loss orders
- Position sizing based on account equity and volatility
- AI can adjust position sizes based on risk assessment
- Trade logging for audit trail

### Performance Optimization
- Async operations for all external API calls
- Bulk data fetching where possible
- Caching layer for frequently accessed data
- Background jobs for non-critical tasks
- AI analysis cached for repeated signals

## Testing Approach

- **Unit Tests**: Test strategies with mock data
- **Integration Tests**: Test broker API interactions
- **Backtesting**: Use at least 2 years of historical data
- **Paper Trading**: Run for minimum 30 days before live deployment

## Security Considerations

- All API keys stored as environment variables
- Webhook authentication required
- Rate limiting on all endpoints
- Trade size limits enforced
- Audit logging for all trades