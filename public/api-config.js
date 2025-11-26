// API Configuration - Switch between local and remote endpoints

// Option 1: Local development (same domain)
const LOCAL_API = '/api/thesidia';

// Option 2: Remote API (your Mac/M4 server)
// Uncomment and set your API URL:
// const REMOTE_API = 'https://api.thesidia.com/api/thesidia';
// const REMOTE_API = 'https://abc123.ngrok.io/api/thesidia';  // ngrok example
// const REMOTE_API = 'https://your-m4-server-ip/api/thesidia';

// Current configuration
// Change this to switch between local and remote
const USE_REMOTE_API = false;  // Set to true to use remote API
const REMOTE_API_URL = 'https://api.thesidia.com/api/thesidia';  // Your remote API URL

// Export the active endpoint
const API_ENDPOINT = USE_REMOTE_API ? REMOTE_API_URL : LOCAL_API;
const STATUS_ENDPOINT = USE_REMOTE_API 
    ? REMOTE_API_URL.replace('/thesidia', '/status')
    : '/api/status';

// For use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_ENDPOINT, STATUS_ENDPOINT };
}

