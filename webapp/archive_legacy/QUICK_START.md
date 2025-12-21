# Thesidia Web App - Quick Start

## Features

✅ **High-End Design**: Black background, white text, grayscale only  
✅ **Mobile-First**: Optimized for mobile devices  
✅ **Security-First**: Input sanitization, rate limiting, secure API  
✅ **Smooth Animations**: Fluid transitions and interactions  
✅ **Advanced Prompt Bar**: Auto-resizing, keyboard shortcuts  
✅ **Grok/GPT-Style UX**: Modern, clean interface  

## Quick Start

### Option 1: Using Start Script (Recommended)

```bash
cd webapp
./start.sh
```

Then open: http://127.0.0.1:5000

### Option 2: Manual Setup

```bash
cd webapp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

## Design Philosophy

- **Black Background**: Pure black (#000000) for deep contrast
- **White Text**: Pure white (#ffffff) for maximum readability
- **Grayscale Only**: No colors, only grays, whites, blacks
- **Smooth Animations**: Cubic-bezier transitions for fluid feel
- **Security-First**: Input sanitization, rate limiting, XSS prevention
- **Mobile-Optimized**: Touch-friendly, responsive design

## Keyboard Shortcuts

- `Enter`: Send message
- `Shift + Enter`: New line
- `Cmd/Ctrl + K`: New conversation
- `Escape`: Close sidebar

## API Endpoint

The app connects to `/api/thesidia` endpoint which:
- Accepts POST requests with `{ message: string, conversation_id: string | null }`
- Returns `{ response: string, timestamp: string }`
- Includes rate limiting (100 requests/minute per IP)
- Includes input sanitization

## Security Features

1. **Input Sanitization**: Removes dangerous characters
2. **Rate Limiting**: 100 requests per minute per IP
3. **XSS Prevention**: Escapes HTML in user input
4. **CORS**: Enabled for secure cross-origin requests
5. **Localhost Only**: Server runs on 127.0.0.1 by default

## Customization

- **Colors**: Edit CSS variables in `styles.css` (`:root` section)
- **API Endpoint**: Change `apiEndpoint` in `app.js` (line 4)
- **Rate Limit**: Change `RATE_LIMIT` in `server.py` (line 20)

## Production Deployment

For production, use a proper WSGI server:

```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 server:app
```

Or use uWSGI, nginx, etc.

## File Structure

```
webapp/
├── index.html      # Main HTML
├── styles.css      # All styles (black/white/gray)
├── app.js          # Frontend JavaScript
├── server.py       # Backend Flask server
├── requirements.txt # Python dependencies
├── start.sh        # Quick start script
└── README.md       # Documentation
```

## Browser Support

- Chrome/Edge (latest)
- Safari (latest)
- Firefox (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Notes

- Server runs on `127.0.0.1:5000` by default
- Conversations saved to browser localStorage
- No external dependencies (except fonts from Google)
- PWA-ready (service worker can be added)

