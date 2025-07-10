# Quick Start Guide - Algo Trader

## 🚀 First Milestone Test

This guide walks you through testing the complete TradingView → Webhook → Backtest flow.

### Prerequisites

- Python 3.8+
- pip installed
- Terminal/Command Prompt

### Step 1: Setup Environment

```bash
# Clone the repository (if not already done)
cd algo-trader

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and set at minimum:
# TRADINGVIEW_WEBHOOK_SECRET="your-secret-here"
# (Optional) ANTHROPIC_API_KEY="your-claude-api-key"
```

### Step 3: Run the Test Flow

#### Option A: Automated Test (Recommended)
```bash
# Run the automated test script
./run_test.sh
```

#### Option B: Manual Test

1. **Start the API server:**
```bash
python main.py
```

2. **In a new terminal, run the test script:**
```bash
python scripts/test_webhook_flow.py
```

### What the Test Does

1. **Health Check** - Verifies API is running
2. **Webhook Test** - Sends a simulated TradingView alert
3. **Backtest** - Runs EMA crossover strategy on synthetic data
4. **Results Display** - Shows performance metrics and trades
5. **AI Analysis** (Optional) - If Claude API key is configured

### Expected Output

```
=== TradingView → Webhook → Backtest Flow Test ===

1. Testing Health Check...
✓ API is healthy
Response: {'status': 'healthy', 'version': '0.1.0', ...}

2. Testing Webhook Endpoint...
Sending buy signal for BTCUSDT
✓ Webhook processed successfully
Alert ID: 123e4567-e89b-12d3-a456-426614174000

3. Running Backtest...
Testing period: 2024-11-11 to 2024-12-11
✓ Backtest completed successfully

4. Backtest Results
┌─────────────────────┬──────────┐
│ Performance Summary │          │
├─────────────────────┼──────────┤
│ Total Trades        │ 15       │
│ Win Rate           │ 53.3%    │
│ Total Return       │ 5.42%    │
│ Sharpe Ratio       │ 1.85     │
│ Max Drawdown       │ -3.21%   │
│ Profit Factor      │ 1.67     │
└─────────────────────┴──────────┘

✅ Test flow completed!
```

### Testing with Real TradingView

1. **Create a Pine Script indicator** (use the template in `scripts/sample_webhook_payloads.json`)

2. **Add an alert in TradingView:**
   - Condition: Your indicator signal
   - Webhook URL: `http://your-server:8000/api/v1/webhook/tradingview`
   - Message: JSON payload (see examples in sample_webhook_payloads.json)

3. **Configure webhook authentication:**
   - Add header: `Authorization: Bearer your-webhook-secret`

### Testing Individual Components

**Test just the webhook:**
```bash
curl -X POST http://localhost:8000/api/v1/webhook/tradingview \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-webhook-secret" \
  -d @scripts/sample_webhook_payloads.json
```

**Test just the backtest:**
```bash
curl -X POST http://localhost:8000/api/v1/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "EMA_CROSSOVER",
    "symbol": "BTCUSDT",
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-01-31T23:59:59",
    "initial_capital": 100000
  }'
```

### Troubleshooting

**API won't start:**
- Check if port 8000 is already in use
- Verify Python version: `python --version`
- Check logs for errors

**Webhook fails:**
- Verify the webhook secret matches in .env and request
- Check the JSON payload format
- Look at API logs for detailed errors

**Backtest returns no trades:**
- The synthetic data might not generate crossovers
- Try adjusting EMA periods in strategy_params
- Extend the backtest period

### Next Steps

1. ✅ Configure real TradingView alerts
2. ✅ Test with paper trading accounts
3. ✅ Add your exchange API keys
4. ✅ Implement additional strategies
5. ✅ Set up the database for persistent storage
6. ✅ Deploy to a cloud server

### Logs and Monitoring

- API logs: Check console output or `logs/` directory
- Webhook logs: Each incoming webhook is logged with timestamp
- Backtest results: Saved in memory (add database for persistence)

Happy Trading! 🚀