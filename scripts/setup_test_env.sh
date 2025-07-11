#!/bin/bash
# Setup script for testing the refactored algo-trader

echo "🚀 Algo Trader Test Environment Setup"
echo "===================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.py first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check Redis
echo -n "Checking Redis... "
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not running"
    echo "Please start Redis: brew services start redis (macOS) or sudo service redis-server start (Linux)"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your configuration"
fi

# Install any missing dependencies
echo "Installing dependencies..."
pip install -q email-validator typer rich

echo ""
echo "Starting services..."
echo "==================="

# Start Celery worker in background
echo "Starting Celery worker..."
celery -A celery_worker worker --loglevel=info &
CELERY_PID=$!
echo "Celery worker PID: $CELERY_PID"

# Start Celery beat in background
echo "Starting Celery beat..."
celery -A celery_worker beat --loglevel=info &
BEAT_PID=$!
echo "Celery beat PID: $BEAT_PID"

# Optional: Start Flower
read -p "Start Flower monitoring UI? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting Flower..."
    celery -A celery_worker flower --port=5555 &
    FLOWER_PID=$!
    echo "Flower PID: $FLOWER_PID (http://localhost:5555)"
fi

echo ""
echo "✅ Services started!"
echo ""
echo "Now you can:"
echo "1. Start the API server: python main.py"
echo "2. Run the test script: python scripts/test_refactoring.py"
echo ""
echo "To stop services:"
echo "kill $CELERY_PID $BEAT_PID ${FLOWER_PID:-}"