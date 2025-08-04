#!/bin/bash
# Integration test script for AMS UI

set -e

echo "=== AMS UI Integration Test ==="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if API server is running
echo -e "${YELLOW}Checking if API server is accessible...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo -e "${GREEN}✓ API server is running${NC}"
else
    echo -e "${RED}✗ API server is not running${NC}"
    echo "Please start the API server with: poetry run uvicorn src.server.app:app --reload"
    exit 1
fi

# Start frontend in background
echo -e "${YELLOW}Starting frontend server...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

# Check if frontend is running
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 | grep -q "200"; then
    echo -e "${GREEN}✓ Frontend server is running${NC}"
else
    echo -e "${RED}✗ Frontend server failed to start${NC}"
    kill $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${GREEN}=== Integration Test Complete ===${NC}"
echo ""
echo "Both servers are running successfully!"
echo ""
echo "📊 Dashboard: http://localhost:5173"
echo "🔧 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the frontend server"

# Wait for user to stop
wait $FRONTEND_PID