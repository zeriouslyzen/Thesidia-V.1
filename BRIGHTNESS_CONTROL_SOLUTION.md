# Brightness Control Solution

## Status
ddcctl is installed but encountering a permissions issue with WindowServer. This is common on newer macOS versions.

## Solution: Use MonitorControl (GUI App - Recommended!)

MonitorControl is easier to use and works better with macOS security:

### Install MonitorControl:
```bash
brew install --cask monitorcontrol
```

Then:
1. Open **MonitorControl** from Applications
2. It appears in your menu bar (top right)
3. Click it to see brightness sliders for all monitors
4. Adjust brightness with sliders - much easier than command line!

## Alternative: Fix ddcctl Permissions

If you want to use ddcctl, you may need to:

1. **Grant Terminal Full Disk Access:**
   - System Settings > Privacy & Security > Full Disk Access
   - Add Terminal (or iTerm if you use that)
   - Restart Terminal

2. **Try with sudo (may work):**
   ```bash
   sudo ddcctl -d 1 -b 50
   ```

3. **Check if monitors support DDC/CI:**
   - Some monitors don't support software brightness control
   - Check your monitor's menu/settings

## Quick Test

Try this to see if it works:
```bash
# Try setting brightness (may need sudo)
sudo ddcctl -d 1 -b 50

# Or try without sudo first
ddcctl -d 1 -b 50
```

## Best Option: MonitorControl

I recommend installing MonitorControl - it's a GUI app that:
- Works better with macOS security
- Shows sliders in menu bar
- Easier to use
- Handles permissions automatically

Install it:
```bash
brew install --cask monitorcontrol
```

Then just open it from Applications and use the menu bar sliders!
