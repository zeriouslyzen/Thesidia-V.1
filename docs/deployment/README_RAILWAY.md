# Railway Deployment Guide

## Quick Start

1. Connect your GitHub repo to Railway
2. Railway will automatically detect the Python project
3. The `Procfile` and `railway.json` will configure the start command
4. Railway will use gunicorn to run the Flask app

## Configuration Files

- **Procfile**: Defines the web process using gunicorn
- **railway.json**: Railway-specific configuration
- **webapp/requirements.txt**: Includes gunicorn for production server

## Environment Variables

Railway will automatically set:
- `PORT`: The port to bind to (Railway provides this)

Optional environment variables you can set:
- `DEV_MODE`: Set to `true` for development mode (relaxes security)
- `PROD_MODE`: Set to `true` for production mode (enables full security)

## Important Notes

⚠️ **Ollama Requirement**: Thesidia requires Ollama to be running. Railway supports persistent services, but you'll need to:

1. Install Ollama in your Railway service, OR
2. Use a separate Railway service for Ollama, OR  
3. Use an external Ollama instance

For full functionality, ensure Ollama is accessible at `http://localhost:11434` or configure the Ollama connection.

## Troubleshooting

If the app doesn't start:
- Check Railway logs for errors
- Ensure `gunicorn` is in `webapp/requirements.txt`
- Verify the `Procfile` points to the correct path (`webapp/server:app`)
- Check that the PORT environment variable is set (Railway does this automatically)

