# Thesidia Web App

High-end mobile web application for interacting with Thesidia - security-first, sleek design with black background and customizable neon color themes.

## Features

### Core Features
- **Modern UI**: Black background with customizable neon color themes (White, Yellow, Green, Purple, Pink)
- **Mobile-First**: Optimized for mobile devices with responsive design
- **Security-First**: Input sanitization, secure API calls, HTTPS support
- **Smooth Animations**: Fluid transitions and interactions (0.3s cubic-bezier)
- **Advanced Prompt Bar**: Auto-resizing, keyboard shortcuts
- **Conversation Management**: Save and load conversations
- **Real-time Responses**: Streaming-like experience

### UI/UX Features
- **Slide-Over Sidebar**: Fixed-position sidebar that slides in from left, pushes content (doesn't compress)
- **Global Color Themes**: 5 neon color options that apply to titles, names, icons, and borders
- **Panoramic Content View**: Main content maintains full width when sidebar opens, just shifts position
- **Theme Persistence**: Color theme preferences saved to localStorage
- **Smooth Transitions**: 0.3s transitions with Material Design easing curves

## Architecture

### Frontend Structure
```
webapp/
├── index.html          # Main contexts page
├── stream.html         # Stream/social feed page
├── app.js             # Main application logic
├── styles.css         # Global styles with CSS variables
├── server.py          # Flask backend server
└── requirements.txt   # Python dependencies
```

### Key Components

#### 1. Sidebar System (`app.js`, `styles.css`)
- **Position**: Fixed to viewport (always `position: fixed`)
- **Width**: 55% mobile / 240px max desktop
- **Behavior**: Slides in from left, pushes main content right (doesn't compress)
- **State Management**: Uses `.open` class on sidebar, `.sidebar-pushed` on `#app`
- **Transitions**: 0.3s cubic-bezier(0.4, 0, 0.2, 1)

#### 2. Color Theme System (`app.js`, `styles.css`)
- **CSS Variables**: `--theme-neon`, `--theme-neon-glow`, `--theme-neon-border`
- **Theme Classes**: `.theme-yellow`, `.theme-green`, `.theme-purple`, `.theme-pink`
- **Applied To**: Titles, names, icons, borders (excludes sidebar menu and usernames)
- **Storage**: localStorage key `thesidia_color_theme`
- **Initialization**: `initColorTheme()` called in `ThesidiaApp.init()`

#### 3. Content Layout
- **Main Container**: `#app` with flex layout
- **Sidebar Open**: `margin-left: 240px` (desktop) or `55%` (mobile)
- **Content Width**: Always `100%` - maintains size, just shifts position
- **No Compression**: Content stays full width, doesn't shrink

### Technical Stack

#### Frontend
- **Vanilla JavaScript**: No frameworks, pure ES6+ classes
- **CSS Variables**: Theme system and design tokens
- **CSS Grid/Flexbox**: Modern layout system
- **LocalStorage**: User preferences and conversations

#### Backend
- **Flask**: Python web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Ollama**: Local LLM integration
- **HTTPS**: Self-signed certificates for development

## Setup

### Prerequisites
- Python 3.8+
- Node.js (optional, for development tools)
- Ollama running locally (for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd thesidia-ice/webapp
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate SSL certificate (for HTTPS)**
   ```bash
   openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=localhost"
   ```

5. **Start the server**
   ```bash
   python3 server.py
   # Or use the start script:
   ./start.sh
   ```

6. **Access the app**
   - Local: `https://localhost:5002`
   - Network: `https://<your-ip>:5002` (for mobile access)

### Configuration

#### API Endpoint (`app.js`)
```javascript
this.apiEndpoint = '/api/thesidia';
this.statusEndpoint = '/api/status';
```

#### Server Port (`server.py`)
- Default: Port 5002
- Auto-detects free port if 5002 is taken
- Binds to `0.0.0.0` for network access

## How It Works

### Sidebar Toggle Flow
1. User clicks menu button (`#menuBtn`)
2. `toggleLeftSidebar()` called
3. Adds `.open` class to `#leftSidebar`
4. Adds `.sidebar-pushed` class to `#app`
5. CSS transitions handle smooth animation
6. Content shifts right via `margin-left`, maintains `width: 100%`

### Color Theme Flow
1. User selects theme in sidebar
2. `setColorTheme(theme)` called
3. Removes all theme classes from `body` and `html`
4. Adds new theme class (e.g., `theme-yellow`)
5. CSS variables update automatically
6. Theme saved to localStorage
7. Theme persists across sessions

### Content Push Mechanism
- **Sidebar**: `position: fixed`, `left: 0`, `transform: translateX(-100%)` when closed
- **Sidebar Open**: `transform: translateX(0)`
- **Main Content**: `margin-left: 240px` (desktop) or `55%` (mobile)
- **Content Width**: Always `100%` - never compressed
- **Result**: Content slides right, maintains full width

## API Endpoints

### POST `/api/thesidia`
Main interaction endpoint
- **Request**: `{ message: string, conversation_id: string | null }`
- **Response**: Streaming SSE events or `{ response: string }`

### GET `/api/status`
System status check
- **Response**: `{ ollama_status: bool, thesidia_ready: bool, model: string }`

### GET `/api/stream/feed`
Stream feed endpoint
- **Query Params**: `page`, `limit`
- **Response**: `{ items: [], has_more: bool, page: int, limit: int }`

## Security Features

- **Input Sanitization**: XSS prevention on all user inputs
- **HTTPS**: Self-signed certificates for development
- **CORS**: Configured for secure cross-origin requests
- **Local Storage**: User data stored locally (can be moved to backend)

## Browser Support

- Modern browsers (Chrome, Safari, Firefox, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- HTTPS required (self-signed cert warning on first visit)
- PWA-ready (service worker can be added)

## Customization

### Colors
Edit CSS variables in `styles.css`:
```css
:root {
    --theme-neon: #ffffff;
    --theme-neon-glow: rgba(255, 255, 255, 0.15);
    --theme-neon-border: rgba(255, 255, 255, 0.15);
}
```

### Sidebar Width
Edit in `styles.css`:
```css
.left-sidebar {
    width: 55%;        /* Mobile */
    max-width: 240px;  /* Desktop */
}
```

### API Endpoint
Change `apiEndpoint` in `app.js` or use `api-config.js`

## Development

### Running Locally
```bash
cd webapp
python3 server.py
```

### Network Access (Mobile Testing)
1. Server binds to `0.0.0.0` by default
2. Find your IP: `ifconfig | grep "inet "`
3. Access from phone: `https://<your-ip>:5002`
4. Accept self-signed certificate warning

### Debugging
- Check browser console for JavaScript errors
- Server logs: `/tmp/thesidia_server.log`
- Check network tab for API calls

## Recent Updates

### Sidebar Improvements
- Fixed large left space when retracted
- Smooth 0.3s transitions (was 0.7s)
- Fixed positioning for no reflow glitches
- Panoramic content view (content doesn't compress)
- Narrower sidebar (55% mobile, 240px desktop)

### Color Theme System
- 5 neon color options (White, Yellow, Green, Purple, Pink)
- Subtle glow effects (reduced from cartoonish brightness)
- Theme selector in sidebar settings
- localStorage persistence
- Excludes sidebar menu and usernames from theming

### Performance
- Cache-busting headers for HTML/CSS/JS
- Optimized transitions with `will-change`
- Material Design easing curves

## Troubleshooting

### Sidebar not opening
- Check browser console for JavaScript errors
- Verify `#menuBtn` and `#leftSidebar` exist in HTML
- Check CSS classes are applied correctly

### Theme not applying
- Check localStorage for `thesidia_color_theme`
- Verify CSS variables are defined
- Check browser console for errors

### Content compressed when sidebar opens
- Verify `#app.sidebar-pushed` has `width: 100%` (not `calc(100% - 240px)`)
- Check mobile media query has `width: 100%`

### Can't access from phone
- Check macOS firewall allows Python
- Verify server binds to `0.0.0.0` (not `127.0.0.1`)
- Check phone is on same Wi-Fi network
- Accept self-signed certificate warning

## License

[Your License Here]

## Contributing

[Contributing Guidelines Here]
