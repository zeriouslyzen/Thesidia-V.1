
import os
import sys
import threading
import time
from pyngrok import ngrok, conf

def start_tunnel():
    """
    Start an ngrok tunnel to the local server port (5002)
    and print the public URL.
    """
    # Configure ngrok to be silent in logs if desired, or verbose
    # conf.get_default().log_event_callback = lambda log: print(str(log))
    
    # Port must match where server.py is running
    PORT = 5002
    
    print(f"[*] Starting ngrok tunnel on port {PORT}...")
    
    try:
        # Open a HTTP tunnel on the default port 5002
        # If you have an auth token, set it in environment variable NGROK_AUTHTOKEN
        # or run `ngrok config add-authtoken <token>` in terminal beforehand.
        public_url = ngrok.connect(PORT).public_url
        print(f"\n✅ PUBLIC API URL: {public_url}")
        print(f"👉 Update your website configuration to use this URL.")
        print(f"   (Keep this script running to keep the tunnel open)\n")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down tunnel...")
            ngrok.kill()
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        print("Tip: If you need an auth token, create a free account at ngrok.com")

if __name__ == "__main__":
    start_tunnel()
