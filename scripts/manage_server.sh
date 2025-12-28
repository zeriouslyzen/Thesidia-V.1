#!/bin/bash

# Katanx Server Management Utility
# Handles clean startups by killing zombie processes first

PORT=5000
CMD="python3 webapp/server.py"

clean_zombies() {
    echo "🔍 Checking for zombie processes..."
    
    # Kill by port
    PID_PORT=$(lsof -t -i:$PORT)
    if [ ! -z "$PID_PORT" ]; then
        echo "⚠️ Killing process $PID_PORT on port $PORT..."
        kill -9 $PID_PORT
    fi

    # Kill by name (more aggressive for zombies)
    # Using [p]ython to avoid grep finding itself
    ZOMBIES=$(ps aux | grep "[p]ython.*server.py" | awk '{print $2}')
    if [ ! -z "$ZOMBIES" ]; then
        echo "⚠️ Killing zombie processes: $ZOMBIES"
        kill -9 $ZOMBIES
    fi
    
    echo "✅ Workspace clean."
}

start_server() {
    clean_zombies
    echo "🚀 Starting Katanx Server..."
    $CMD
}

stop_server() {
    clean_zombies
    echo "🛑 Server stopped."
}

status() {
    echo "=== System Status ==="
    ps aux | grep "[p]ython.*server.py" || echo "No server running."
    lsof -i:$PORT || echo "Port $PORT is free."
}

case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        start_server
        ;;
    status)
        status
        ;;
    clean)
        clean_zombies
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|clean}"
        exit 1
esac
