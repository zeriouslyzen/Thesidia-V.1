#!/bin/bash
# Setup script for Thesidia Enhanced

echo "Setting up Thesidia Enhanced..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install --user ollama chromadb requests beautifulsoup4 lxml

echo ""
echo "Setup complete!"
echo ""
echo "To run Thesidia Enhanced:"
echo "  python3 thesidia_enhanced.py"
echo ""

