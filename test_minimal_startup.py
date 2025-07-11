#!/usr/bin/env python3
"""Minimal test to verify the server can start after refactoring."""
import os
import sys

# Set minimal environment variables
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
os.environ.setdefault("TRADINGVIEW_WEBHOOK_SECRET", "test-secret")
os.environ.setdefault("SECRET_KEY", "test-secret-key-change-in-production")

# Test imports
print("Testing imports...")
try:
    from app.core.config import settings
    print("✅ Config loaded")
    
    from app.core.telemetry import get_logger, metrics
    print("✅ Telemetry loaded")
    
    from main import app
    print("✅ FastAPI app created")
    
    # Check all routers are included
    routes = [route.path for route in app.routes]
    print(f"\n📍 Registered routes: {len(routes)}")
    
    # Check for new endpoints
    new_endpoints = [
        "/api/v1/auth/register",
        "/api/v1/profile/risk-assessment", 
        "/api/v1/tasks/backtest",
        "/api/v1/webhook/tradingview"
    ]
    
    for endpoint in new_endpoints:
        # Check if any route matches the endpoint pattern
        found = any(endpoint in route.path for route in app.routes)
        status = "✅" if found else "❌"
        print(f"{status} {endpoint}")
    
    print("\n✅ All imports successful! Server should start normally.")
    print("\nTo start the server:")
    print("  python main.py")
    print("\nOr with uvicorn:")
    print("  uvicorn main:app --reload")
    
except Exception as e:
    print(f"\n❌ Import error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you're in the virtual environment")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Check your .env file exists")
    sys.exit(1)