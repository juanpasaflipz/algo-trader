"""Pytest configuration and fixtures."""
import pytest
import os
from typing import Generator
from fastapi.testclient import TestClient


# Set test environment variables
os.environ["ENVIRONMENT"] = "testing"
os.environ["TRADINGVIEW_WEBHOOK_SECRET"] = "test_secret"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    from main import app as _app

    return _app


@pytest.fixture
def client(app) -> Generator:
    """Create test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def authorized_client(client) -> TestClient:
    """Create test client with authorization headers."""
    client.headers = {
        "Authorization": f"Bearer {os.environ['TRADINGVIEW_WEBHOOK_SECRET']}"
    }
    return client


@pytest.fixture
def sample_trade_signal():
    """Sample trade signal for testing."""
    return {
        "strategy": "EMA_Crossover",
        "symbol": "BTCUSDT",
        "signal": "buy",
        "price": 50000.0,
        "quantity": 0.1,
        "stop_loss": 49000.0,
        "take_profit": 52000.0,
        "comment": "Test signal",
    }


@pytest.fixture
def sample_backtest_request():
    """Sample backtest request for testing."""
    return {
        "strategy": "EMA_Crossover",
        "symbol": "BTCUSDT",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_capital": 10000.0,
        "parameters": {"fast_period": 12, "slow_period": 26},
    }
