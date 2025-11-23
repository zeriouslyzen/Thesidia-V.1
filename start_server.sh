#!/bin/bash
# Start Thesidia server with virtual environment

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start server
cd webapp
python3 server.py

