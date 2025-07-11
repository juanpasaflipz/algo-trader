#!/usr/bin/env python3
"""Test script to verify .env file is properly formatted."""
import os
import sys

# Clear any cached environment variables
if 'IBKR_PORT' in os.environ:
    del os.environ['IBKR_PORT']
if 'BACKTEST_COMMISSION' in os.environ:
    del os.environ['BACKTEST_COMMISSION']

# Force reload of dotenv
from dotenv import load_dotenv
load_dotenv(override=True)

# Now test the imports
print("Testing imports with fresh environment...")
try:
    from app.core.config import settings
    print("✅ Config loaded successfully")
    print(f"  - IBKR_PORT: {settings.ibkr_port}")
    print(f"  - BACKTEST_COMMISSION: {settings.backtest_commission}")
    
    from main import app
    print("✅ FastAPI app created")
    
    print("\n✅ All imports successful! The .env file is now properly formatted.")
    
except Exception as e:
    print(f"\n❌ Import error: {e}")
    print("\nChecking .env file directly...")
    with open('.env', 'r') as f:
        for line in f:
            if 'IBKR_PORT' in line or 'BACKTEST_COMMISSION' in line:
                print(f"  {line.strip()}")