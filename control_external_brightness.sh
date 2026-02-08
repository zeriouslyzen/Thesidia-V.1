#!/bin/bash

# Script to control external monitor brightness
# This can help reduce WindowServer CPU usage

echo "=========================================="
echo "External Monitor Brightness Control"
echo "=========================================="
echo ""

# Check if ddcctl is installed (best tool for external monitors)
if command -v ddcctl &> /dev/null; then
    echo "Using ddcctl..."
    echo ""
    echo "Available commands:"
    echo "  bash control_external_brightness.sh up    - Increase brightness"
    echo "  bash control_external_brightness.sh down  - Decrease brightness"
    echo "  bash control_external_brightness.sh set 50 - Set to 50%"
    echo ""
    
    ACTION=${1:-help}
    
    case $ACTION in
        up)
            echo "Increasing brightness on all external monitors..."
            ddcctl -d 1 -b +10 2>/dev/null
            ddcctl -d 2 -b +10 2>/dev/null
            echo "Brightness increased"
            ;;
        down)
            echo "Decreasing brightness on all external monitors..."
            ddcctl -d 1 -b -10 2>/dev/null
            ddcctl -d 2 -b -10 2>/dev/null
            echo "Brightness decreased"
            ;;
        set)
            LEVEL=${2:-50}
            echo "Setting brightness to ${LEVEL}% on all external monitors..."
            ddcctl -d 1 -b ${LEVEL} 2>/dev/null
            ddcctl -d 2 -b ${LEVEL} 2>/dev/null
            echo "Brightness set to ${LEVEL}%"
            ;;
        *)
            echo "Usage: $0 [up|down|set LEVEL]"
            echo ""
            echo "To install ddcctl:"
            echo "  brew install ddcctl"
            ;;
    esac
else
    echo "ddcctl not found. Installing or using alternative method..."
    echo ""
    
    # Check if Homebrew is installed
    if command -v brew &> /dev/null; then
        echo "Installing ddcctl via Homebrew..."
        read -p "Install ddcctl? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            brew install ddcctl
            echo ""
            echo "Installation complete! Run this script again."
        else
            echo "Installation cancelled."
        fi
    else
        echo "Homebrew not found. Here are your options:"
        echo ""
        echo "Option 1: Install Homebrew, then ddcctl"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "  brew install ddcctl"
        echo ""
        echo "Option 2: Use macOS built-in brightness (limited to built-in display)"
        echo "  This script will use AppleScript for built-in display only"
        echo ""
        
        # Use AppleScript for built-in display
        ACTION=${1:-help}
        case $ACTION in
            up)
                osascript -e "tell application \"System Events\" to key code 144" 2>/dev/null
                echo "Built-in display brightness increased"
                ;;
            down)
                osascript -e "tell application \"System Events\" to key code 145" 2>/dev/null
                echo "Built-in display brightness decreased"
                ;;
            *)
                echo "For external monitors, you need ddcctl."
                echo "Install Homebrew first, then: brew install ddcctl"
                ;;
        esac
    fi
fi
