#!/bin/bash

# Kill all stuck indexing processes
# Run: bash kill_all_indexing.sh

echo "Killing all indexing-related processes..."

# Kill Spotlight processes
killall -9 corespotlightd 2>/dev/null
killall -9 mdsync 2>/dev/null
killall -9 mdworker 2>/dev/null
killall -9 mdbulkimport 2>/dev/null

# Kill app-specific indexing extensions
killall -9 "com.apple.podcasts.SpotlightIndexExtension" 2>/dev/null

# Kill any other Spotlight extensions
pkill -9 -f "SpotlightIndexExtension" 2>/dev/null

echo ""
echo "Done! Checking what's left..."
ps aux | grep -E "(index|spotlight|mdsync|mdworker|corespotlight)" | grep -v grep || echo "✅ No indexing processes found"

echo ""
echo "Note: Some processes may restart, but they should use less CPU"
echo "since Spotlight indexing is disabled."
