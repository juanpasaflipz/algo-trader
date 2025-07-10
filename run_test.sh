#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Algo Trader Test Runner ===${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${RED}Please edit .env file and add your configuration!${NC}"
    echo -e "${YELLOW}Especially the TRADINGVIEW_WEBHOOK_SECRET${NC}"
fi

# Start the API server in background
echo -e "${BLUE}Starting API server...${NC}"
python main.py &
API_PID=$!

# Wait for server to start
echo -e "${YELLOW}Waiting for server to start...${NC}"
sleep 5

# Run the test script
echo -e "${GREEN}Running test workflow...${NC}"
python scripts/test_webhook_flow.py

# Kill the API server
echo -e "${BLUE}Stopping API server...${NC}"
kill $API_PID

echo -e "${GREEN}Test completed!${NC}"