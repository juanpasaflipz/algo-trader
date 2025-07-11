#!/usr/bin/env python3
"""Run the application with proper environment handling."""
import os
import sys
from pathlib import Path

# Ensure we're in the correct directory
os.chdir(Path(__file__).parent)

# Force reload of .env file
from dotenv import load_dotenv
load_dotenv(override=True)

# Import and run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )