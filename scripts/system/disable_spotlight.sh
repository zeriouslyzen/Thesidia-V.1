#!/bin/bash

# Script to completely disable Spotlight on macOS
# Run with: bash disable_spotlight.sh

echo "Disabling Spotlight indexing..."
sudo mdutil -a -i off

echo "Killing Spotlight processes..."
sudo killall corespotlightd mdsync mdworker 2>/dev/null

echo "Unloading Spotlight launch daemons..."
sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.metadata.mds.plist 2>/dev/null
sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.mds.scan.plist 2>/dev/null
sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.mds.storewriter.plist 2>/dev/null

echo "Removing Spotlight index files..."
sudo rm -rf ~/.Spotlight-V100
sudo rm -rf ~/Library/Metadata/CoreSpotlight
sudo rm -rf /Volumes/*/.Spotlight-V100 2>/dev/null

echo "Preventing Spotlight from restarting..."
# Add to /etc/hostfile to block Spotlight (optional, more aggressive)
# sudo sh -c 'echo "127.0.0.1 com.apple.metadata.mds" >> /etc/hosts'

echo ""
echo "Spotlight has been disabled."
echo "To verify, run: mdutil -a -s"
echo ""
echo "Note: You may need to restart your Mac for all changes to take full effect."
echo "Spotlight search in Finder will no longer work, but you can still use 'find' command in Terminal."
