#!/bin/bash

echo "Starting Algo Trader Platform..."

# Start backend in background
echo "Starting backend server..."
source venv/bin/activate
python fix_env.py &
BACKEND_PID=$!

# Give backend time to start
sleep 2

# Start frontend
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Algo Trader Platform is running!"
echo ""
echo "📊 Frontend: http://localhost:5173"
echo "🚀 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait