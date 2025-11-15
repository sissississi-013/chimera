#!/bin/bash

# Chimera Setup Script
# This script sets up both backend and frontend for development

echo "🧬 Setting up Chimera - Autonomous Drug Discovery Agent"
echo "========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "\n${YELLOW}Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check Node.js
echo -e "\n${YELLOW}Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js 18 or higher.${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"

# Setup Backend
echo -e "\n${YELLOW}Setting up backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend setup complete${NC}"
else
    echo -e "${RED}✗ Backend setup failed${NC}"
    exit 1
fi

cd ..

# Setup Frontend
echo -e "\n${YELLOW}Setting up frontend...${NC}"
cd frontend

echo "Installing Node dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend setup complete${NC}"
else
    echo -e "${RED}✗ Frontend setup failed${NC}"
    exit 1
fi

cd ..

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "\nTo start the application:"
echo -e "  ${YELLOW}./run.sh${NC}  (starts both backend and frontend)"
echo -e "\nOr manually:"
echo -e "  ${YELLOW}Terminal 1:${NC} cd backend && python -m uvicorn api.main:app --reload"
echo -e "  ${YELLOW}Terminal 2:${NC} cd frontend && npm run dev"
