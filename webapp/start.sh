#!/bin/bash
# Start Thesidia Web App Server

echo "Starting Thesidia Web App..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Also install main project requirements if exists
if [ -f "../requirements.txt" ]; then
    echo "Installing main project dependencies..."
    pip install -q -r ../requirements.txt
fi

# Start server
echo ""
echo "Server starting on http://127.0.0.1:5000"
echo "Press Ctrl+C to stop"
echo ""
python3 server.py

