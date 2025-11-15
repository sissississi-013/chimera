#!/bin/bash

# Chimera Run Script
# Starts both backend and frontend servers

echo "🧬 Starting Chimera..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup INT TERM

# Start backend
echo -e "${YELLOW}Starting backend on http://localhost:8000${NC}"
cd backend
source venv/bin/activate 2>/dev/null || true
python -m uvicorn api.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${YELLOW}Starting frontend on http://localhost:3000${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}✓ Chimera is running!${NC}"
echo -e "\n  Backend:  ${YELLOW}http://localhost:8000${NC}"
echo -e "  Frontend: ${YELLOW}http://localhost:3000${NC}"
echo -e "  API Docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop${NC}"
echo -e "${GREEN}=========================================${NC}\n"

# Wait for processes
wait
