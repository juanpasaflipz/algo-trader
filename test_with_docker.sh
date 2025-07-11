#!/bin/bash
# Test the refactored algo-trader using Docker Compose

echo "🐳 Testing Algo Trader with Docker Compose"
echo "=========================================="

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

# Build the containers
echo "Building containers..."
docker-compose build

# Start all services
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "Service Status:"
echo "==============="
docker-compose ps

# Show logs from the last minute
echo ""
echo "Recent Logs:"
echo "============"
docker-compose logs --tail=20

echo ""
echo "✅ Services are running!"
echo ""
echo "Access points:"
echo "- API: http://localhost:8000/docs"
echo "- Flower (Celery monitoring): http://localhost:5555"
echo "- Prometheus metrics: http://localhost:9090"
echo ""
echo "To run tests:"
echo "  python scripts/test_refactoring.py"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop all services:"
echo "  docker-compose down"