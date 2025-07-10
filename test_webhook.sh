#!/bin/bash
# Test TradingView webhook endpoint

# Your webhook secret from .env
WEBHOOK_SECRET="ABC123"

# Test payload
curl -X POST http://127.0.0.1:9999/api/v1/webhook/tradingview \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $WEBHOOK_SECRET" \
  -d '{
    "strategy": "EMA_Crossover",
    "symbol": "BTCUSDT",
    "signal": "buy",
    "price": 50000.0,
    "quantity": 0.1,
    "stop_loss": 49000.0,
    "take_profit": 52000.0,
    "comment": "Test webhook alert"
  }'