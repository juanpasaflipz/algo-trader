#!/bin/bash

echo "🚀 Quick Setup for Algo Trader"
echo ""

# Remove old venv if exists
if [ -d "venv" ]; then
    echo "Removing old virtual environment..."
    rm -rf venv
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate it
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install minimal requirements
echo "Installing minimal dependencies..."
pip install -r requirements-minimal.txt

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start testing:"
echo "1. Edit .env file and set TRADINGVIEW_WEBHOOK_SECRET"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python main.py"
echo ""
echo "In another terminal:"
echo "1. Run: source venv/bin/activate"
echo "2. Run: python scripts/test_webhook_flow.py"