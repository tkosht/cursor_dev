#!/bin/bash
# Development servers startup script with 0.0.0.0 binding

set -e

echo "=== Starting AMS Development Servers ==="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')

# Start backend
echo -e "${YELLOW}Starting Backend API Server...${NC}"
cd "$(dirname "$0")/.."
poetry run uvicorn src.server.app:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${YELLOW}Starting Frontend Dev Server...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

echo ""
echo -e "${GREEN}=== Servers Started Successfully ===${NC}"
echo ""
echo "Access from this machine:"
echo "  📊 Dashboard: http://localhost:5173"
echo "  🔧 API: http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Access from network:"
echo "  📊 Dashboard: http://${LOCAL_IP}:5173"
echo "  🔧 API: http://${LOCAL_IP}:8000"
echo "  📚 API Docs: http://${LOCAL_IP}:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Stopping servers...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}Servers stopped${NC}"
}

# Set trap to cleanup on Ctrl+C
trap cleanup EXIT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID