# Thesidia Web App

High-end mobile web application for interacting with Thesidia - security-first, sleek design with black background and white text.

## Features

- **Modern UI**: Black background, white text, grayscale only
- **Mobile-First**: Optimized for mobile devices
- **Security-First**: Input sanitization, secure API calls
- **Smooth Animations**: Fluid transitions and interactions
- **Advanced Prompt Bar**: Auto-resizing, keyboard shortcuts
- **Conversation Management**: Save and load conversations
- **Real-time Responses**: Streaming-like experience

## Setup

1. Serve the files through a web server (required for API calls)
2. Configure API endpoint in `app.js` (line 4)
3. Ensure backend API is running at configured endpoint

## Backend Integration

The app expects a POST endpoint at `/api/thesidia` with:
- Request: `{ message: string, conversation_id: string | null }`
- Response: `{ response: string }` or `{ message: string }`

## Security Features

- Input sanitization
- XSS prevention
- Secure API communication
- Local storage for conversations (can be moved to backend)

## Browser Support

- Modern browsers (Chrome, Safari, Firefox, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- PWA-ready (service worker can be added)

## Customization

- Colors: Edit CSS variables in `styles.css`
- API endpoint: Change `apiEndpoint` in `app.js`
- Features: Extend `ThesidiaApp` class

