#!/bin/bash
# Development Server Launcher for Thesidia Web App
# This script sets up and runs the Flask development server

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Thesidia Development Server${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"

# Check/create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}✓${NC} Activating virtual environment"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install -q --upgrade pip

# Install/update dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} requirements.txt not found"
fi

# Set default port (can be overridden with PORT env var)
export PORT=${PORT:-5002}

# Kill any existing server on this port
echo -e "${YELLOW}Checking for existing server on port ${PORT}...${NC}"
if lsof -ti:${PORT} > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠${NC} Port ${PORT} is in use. Attempting to free it..."
    pkill -f "python.*server.py" 2>/dev/null || true
    sleep 1
fi

# Display server info
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Starting development server...${NC}"
echo ""
echo -e "  ${BLUE}Local:${NC}    http://localhost:${PORT}"
echo -e "  ${BLUE}Network:${NC}  http://$(hostname -I | awk '{print $1}'):${PORT}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Run the server
python3 server.py

