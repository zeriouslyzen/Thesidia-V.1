#!/bin/bash
# Start Thesidia server with virtual environment

cd "$(dirname "$0")"

# Kill any existing server processes
echo "Checking for existing server processes..."
pkill -f "python.*server.py" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Killed existing server processes"
    sleep 1
else
    echo "No existing server processes found"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start server
cd webapp
python3 server.py

