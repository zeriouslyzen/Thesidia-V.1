#!/bin/bash

# Quick install script for external monitor brightness control

echo "Installing brightness control tools..."
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH (for Apple Silicon Macs)
    if [ -f /opt/homebrew/bin/brew ]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi

echo ""
echo "Installing ddcctl..."
brew install ddcctl

echo ""
echo "Installation complete!"
echo ""
echo "Usage:"
echo "  bash control_external_brightness.sh up    - Increase brightness"
echo "  bash control_external_brightness.sh down  - Decrease brightness"
echo "  bash control_external_brightness.sh set 50 - Set to 50%"
echo ""
echo "Or use ddcctl directly:"
echo "  ddcctl -d 1 -b 50  # Set display 1 to 50%"
echo "  ddcctl -d 2 -b 50  # Set display 2 to 50%"
