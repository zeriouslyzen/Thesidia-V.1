# How to Control External Monitor Brightness

## The Problem
External monitors (P2-R and P2-L) don't have built-in macOS brightness controls. This script will let you control them programmatically, which can also help reduce WindowServer CPU usage.

## Installation

### Step 1: Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install ddcctl
```bash
brew install ddcctl
```

## Usage

After installation, use the script:

```bash
# Increase brightness
bash "/Users/deshonjackson/thesidia ice/control_external_brightness.sh" up

# Decrease brightness
bash "/Users/deshonjackson/thesidia ice/control_external_brightness.sh" down

# Set to specific level (0-100)
bash "/Users/deshonjackson/thesidia ice/control_external_brightness.sh" set 50
```

## Direct ddcctl Commands

Once installed, you can also use ddcctl directly:

```bash
# List available displays
ddcctl -d 1

# Set brightness on display 1 to 50%
ddcctl -d 1 -b 50

# Set brightness on display 2 to 50%
ddcctl -d 2 -b 50

# Increase brightness on display 1
ddcctl -d 1 -b +10

# Decrease brightness on display 2
ddcctl -d 2 -b -10
```

## Benefits

1. **Control external monitor brightness** - No more manual monitor buttons
2. **Reduce WindowServer CPU** - Lower brightness = less rendering load
3. **Automation** - Can be scripted or added to shortcuts
4. **Eye strain** - Adjust brightness throughout the day

## Troubleshooting

### If ddcctl doesn't work:
- Some monitors don't support DDC/CI
- Try different display numbers: `ddcctl -d 1`, `ddcctl -d 2`, etc.
- Check monitor settings - DDC/CI may need to be enabled in monitor menu

### Alternative: Monitor Control Apps
If ddcctl doesn't work, try these apps:
- **MonitorControl** (free, GUI app)
- **Lunar** (free/paid, advanced features)
- **Brightness Slider** (free)

Install via:
```bash
brew install --cask monitorcontrol
# or
brew install --cask lunar
```

## Quick Setup Script

Run this to install everything:
```bash
# Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ddcctl
brew install ddcctl

# Test it
ddcctl -d 1
```

## Integration with System

You can create keyboard shortcuts or menu bar apps to control brightness easily. The script can be called from:
- Automator workflows
- Keyboard shortcuts (via Shortcuts app)
- Menu bar apps like MonitorControl
