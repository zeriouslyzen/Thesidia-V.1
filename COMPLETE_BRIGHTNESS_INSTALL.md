# Complete Brightness Control Installation

## Current Status
ddcctl is not installed yet. Let's complete the installation.

## Step-by-Step Installation

### Step 1: Check if Homebrew is installed
Run this in Terminal:
```bash
which brew
```

### Step 2A: If Homebrew is NOT installed
Install Homebrew first:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Important:** Follow the on-screen instructions. You may need to:
- Enter your password
- Press RETURN to continue
- Add Homebrew to your PATH (it will tell you the command)

After Homebrew installs, you may need to run:
```bash
# For Apple Silicon Macs (M1/M2/M3):
eval "$(/opt/homebrew/bin/brew shellenv)"

# For Intel Macs:
eval "$(/usr/local/bin/brew shellenv)"
```

### Step 2B: If Homebrew IS installed
Just install ddcctl:
```bash
brew install ddcctl
```

### Step 3: Test it
```bash
# Check if it works
ddcctl -d 1

# Try setting brightness on display 1 to 50%
ddcctl -d 1 -b 50
```

## Alternative: Use MonitorControl (GUI App - Easier!)

If command line is too complicated, use this GUI app instead:

```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install MonitorControl
brew install --cask monitorcontrol
```

Then:
1. Open MonitorControl from Applications
2. It will appear in your menu bar
3. Click it to see brightness sliders for all monitors
4. Adjust brightness with sliders - much easier!

## Quick Commands to Run

**Copy and paste this entire block into Terminal:**

```bash
# Check if Homebrew exists
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add to PATH
    if [ -f /opt/homebrew/bin/brew ]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
fi

# Install ddcctl
echo "Installing ddcctl..."
brew install ddcctl

# Test it
echo "Testing ddcctl..."
ddcctl -d 1
```

## After Installation

Once ddcctl is installed, you can use:

```bash
# Control brightness
bash "/Users/deshonjackson/thesidia ice/control_external_brightness.sh" up
bash "/Users/deshonjackson/thesidia ice/control_external_brightness.sh" down
bash "/Users/deshonjackson/thesidia ice/control_external_brightness.sh" set 50
```

## Troubleshooting

### If ddcctl doesn't work with your monitors:
- Some monitors don't support DDC/CI
- Try MonitorControl app instead (GUI, easier)
- Check your monitor's menu - may need to enable DDC/CI

### If Homebrew installation fails:
- Make sure you have admin access
- Check your internet connection
- Try running the install command again
