# Development Server Guide

## Quick Start

### Option 1: Using the Dev Server Script (Recommended)
```bash
cd webapp
./dev-server.sh
```

### Option 2: Manual Start
```bash
cd webapp
source venv/bin/activate
python3 server.py
```

### Option 3: Using the Start Script
```bash
cd webapp
./start.sh
```

## Server Configuration

- **Default Port**: 5002
- **Override Port**: Set `PORT` environment variable
  ```bash
  PORT=5000 ./dev-server.sh
  ```

## Access URLs

Once running, access the application at:
- **Local**: http://localhost:5002
- **Network**: http://YOUR_IP:5002 (for mobile device testing)

## Key Pages

- **Home/Stream**: http://localhost:5002/stream
- **Explore/Search**: http://localhost:5002/search
- **KIM Chat**: http://localhost:5002/kim.html
- **KIM Sidebar**: Integrated in stream.html (click Messages button)

## Dependencies

Install dependencies:
```bash
cd webapp
source venv/bin/activate
pip install -r requirements.txt
```

## Troubleshooting

### Port Already in Use
```bash
# Kill existing server
pkill -f "python.*server.py"

# Or use a different port
PORT=5003 ./dev-server.sh
```

### Virtual Environment Issues
```bash
cd webapp
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Missing Dependencies
```bash
cd webapp
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Server Features

- Flask web server with SocketIO support
- Real-time messaging (KIM) via WebSocket
- REST API endpoints
- Static file serving
- HTTPS support (if cert.pem and key.pem exist)

