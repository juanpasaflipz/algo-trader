#!/usr/bin/env python3
"""Minimal server startup for testing"""

from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create minimal FastAPI app
app = FastAPI(
    title="Algo Trader - Minimal", version="0.1.0", docs_url="/docs", redoc_url="/redoc"
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Algo Trader API is running (minimal mode)",
        "webhook_secret_configured": bool(os.getenv("TRADINGVIEW_WEBHOOK_SECRET")),
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "run_minimal:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
