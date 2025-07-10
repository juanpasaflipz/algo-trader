# Algo Trader - AI-Enhanced Algorithmic Trading Platform

A modular algorithmic trading platform with Claude AI integration, TradingView webhooks, backtesting capabilities, and support for multiple exchanges/brokers.

## Features

- **AI-Powered Analysis**: Claude AI integration for trade signal validation and market analysis
- **TradingView Integration**: Receive trading signals via webhooks with AI enhancement
- **Intelligent Risk Management**: AI-powered position sizing and risk assessment
- **Backtesting Engine**: Test strategies on historical data with AI insights
- **Multiple Strategies**: Extensible framework including EMA Crossover and AI-Enhanced strategies
- **Exchange Support**: Ready for Binance, Interactive Brokers, Alpaca integration
- **Market Commentary**: AI-generated market analysis and trading insights
- **RESTful API**: FastAPI-based API for all operations
- **Real-time Monitoring**: Prometheus metrics and structured logging

## Quick Start

### Prerequisites

- Python 3.8+
- Redis (for caching and task queue)
- PostgreSQL (for data persistence)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd algo-trader
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
# IMPORTANT: Add your Anthropic API key for Claude AI features
```

5. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
algo_trader/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Configuration, logging, errors
│   ├── models/          # Pydantic models
│   ├── services/        # Business logic
│   │   ├── strategies/  # Trading strategies
│   │   └── broker_clients/  # Exchange integrations
│   └── jobs/            # Background tasks
├── tests/               # Test suite
├── scripts/             # Utility scripts
└── main.py             # Application entry point
```

## Key Endpoints

### Health & Status
- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - Detailed status

### TradingView Webhook
- `POST /api/v1/webhook/tradingview` - Receive TradingView alerts

### Backtesting
- `POST /api/v1/backtest` - Run a backtest
- `GET /api/v1/backtests` - List all backtests
- `GET /api/v1/strategies` - List available strategies

### Trading Control
- `POST /api/v1/trading/control` - Start/stop strategies
- `GET /api/v1/trading/status` - Get trading status
- `POST /api/v1/trading/emergency-stop` - Emergency shutdown

### AI Analysis
- `POST /api/v1/ai/analyze-trade` - Get AI analysis for a trade signal
- `POST /api/v1/ai/analyze-backtest` - Get AI insights on backtest results
- `POST /api/v1/ai/market-commentary` - Get AI-generated market commentary
- `POST /api/v1/ai/assess-risk` - AI-powered risk assessment
- `POST /api/v1/ai/optimize-strategy` - Get AI strategy optimization suggestions

## Example: Running a Backtest

### Standard Strategy
```bash
curl -X POST http://localhost:8000/api/v1/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "EMA_CROSSOVER",
    "symbol": "BTCUSDT",
    "start_date": "2023-01-01T00:00:00",
    "end_date": "2023-12-31T23:59:59",
    "initial_capital": 100000,
    "strategy_params": {
      "fast_ema_period": 12,
      "slow_ema_period": 26
    }
  }'
```

### AI-Enhanced Strategy
```bash
curl -X POST http://localhost:8000/api/v1/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "AI_ENHANCED",
    "symbol": "BTCUSDT",
    "start_date": "2023-01-01T00:00:00",
    "end_date": "2023-12-31T23:59:59",
    "initial_capital": 100000,
    "strategy_params": {
      "base_strategy_params": {
        "fast_ema_period": 12,
        "slow_ema_period": 26
      },
      "ai_confidence_threshold": 70,
      "ai_weight": 0.5
    }
  }'
```

## Example: AI Trade Analysis

```bash
curl -X POST http://localhost:8000/api/v1/ai/analyze-trade \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "strategy": "EMA_CROSSOVER",
    "signal_type": "buy",
    "price": 50000,
    "quantity": 0.1,
    "stop_loss": 49000,
    "take_profit": 52000,
    "market_context": {
      "trend": "upward",
      "volatility": "medium"
    }
  }'
```

## Development

### Adding a New Strategy

1. Create a new file in `app/services/strategies/`
2. Inherit from `BaseStrategy`
3. Implement required methods:
   - `calculate_indicators()`
   - `generate_signals()`
   - `get_required_lookback()`
4. Register in `Backtester.STRATEGIES`

### Adding a New Exchange

1. Create a client in `app/services/broker_clients/`
2. Implement the broker interface
3. Add configuration in `app/core/config.py`
4. Update `.env.example` with required keys

## Testing

Run tests with:
```bash
pytest tests/
```

## Security Notes

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Webhook endpoints require authentication
- Implement rate limiting in production

## License

[Your License Here]

## Contributing

[Contributing Guidelines]