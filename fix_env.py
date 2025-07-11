#!/usr/bin/env python3
"""Fix environment variables by clearing cache and reloading."""
import os
import sys

# Clear potentially cached environment variables
env_vars_to_clear = ['IBKR_PORT', 'BACKTEST_COMMISSION']
for var in env_vars_to_clear:
    if var in os.environ:
        print(f"Clearing cached {var}: {os.environ[var]}")
        del os.environ[var]

# Now set them correctly before any imports
os.environ['IBKR_PORT'] = '7497'
os.environ['BACKTEST_COMMISSION'] = '0.001'

print("Environment variables set:")
print(f"IBKR_PORT = {os.environ.get('IBKR_PORT')}")
print(f"BACKTEST_COMMISSION = {os.environ.get('BACKTEST_COMMISSION')}")

# Now run the main app
print("\nStarting application...")
import main