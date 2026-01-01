#!/usr/bin/env bash
set -e

echo "🔄 Restarting Thesidia services..."

# Kill stale processes
echo "   Stopping existing server processes..."
pkill -f "python server.py" 2>/dev/null || true
pkill -f "python tunnel.py" 2>/dev/null || true

# Wait for ports to be released
sleep 1

# Set port (use environment variable or default to 5002)
export PORT=${PORT:-5002}

# Change to webapp directory
cd "$(dirname "$0")"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start Flask server in background
echo "   Starting Flask server on port $PORT..."
python server.py &
SERVER_PID=$!

# Wait for server to be ready
echo "   Waiting for server to be ready..."
for i in {1..10}; do
    if curl -s "http://127.0.0.1:$PORT/health" > /dev/null 2>&1; then
        echo "✅ Server is ready on port $PORT"
        break
    fi
    sleep 1
done

# Optionally start tunnel (uncomment if needed)
# echo "   Starting ngrok tunnel..."
# python tunnel.py &

echo ""
echo "🚀 Thesidia is running!"
echo "   Local:  http://127.0.0.1:$PORT"
echo "   Press Ctrl+C to stop"
echo ""

# Keep script running and forward signals to server
trap "kill $SERVER_PID 2>/dev/null; exit" SIGINT SIGTERM
wait $SERVER_PID
