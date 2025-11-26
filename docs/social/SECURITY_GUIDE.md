# Security Guide

## Overview

Thesidia implements a comprehensive security infrastructure that is configured but disabled during development, and fully enabled in production.

## Security Configuration

### Environment Variables

- `DEV_MODE=true` (default): Development mode with relaxed security
- `PROD_MODE=true`: Production mode with full security

### Security Features

#### Development Mode

- **Authentication**: Disabled (uses session-based identification)
- **CSRF Protection**: Disabled
- **Rate Limiting**: Enabled but relaxed (1000 requests/minute)
- **Input Validation**: Basic sanitization
- **Security Headers**: Disabled
- **Password Requirements**: None

#### Production Mode

- **Authentication**: Required (JWT tokens, password hashing)
- **CSRF Protection**: Enabled for state-changing operations
- **Rate Limiting**: Strict (100 requests/minute, 1000/hour)
- **Input Validation**: Strict (length limits, format validation)
- **Security Headers**: Enabled (CSP, HSTS, X-Frame-Options, etc.)
- **Password Requirements**: Minimum 12 characters, letters + numbers

## Authentication System

### Components

- **AuthManager** (`webapp/auth/auth_manager.py`): JWT token generation, password hashing, user authentication
- **SessionManager** (`webapp/auth/session_manager.py`): Session management with expiration and rotation

### Usage

In development mode, authentication is bypassed and the system uses existing session-based identification.

In production mode:
- Users must register with username and password
- Passwords are hashed using bcrypt
- JWT tokens issued for authenticated sessions
- Sessions expire after 7 days
- Maximum 5 concurrent sessions per user

## Security Middleware

### Input Sanitization

All user input is sanitized to prevent:
- XSS attacks (HTML tag removal, entity escaping)
- CSS injection (class name removal)
- Control character injection
- React fragment injection

### Rate Limiting

- Per-IP rate limiting (memory-based in dev, Redis-ready in prod)
- Per-endpoint rate limiting
- Per-user rate limiting
- Rate limit headers in responses

### CSRF Protection

- CSRF tokens generated per session
- Tokens validated for state-changing operations
- 24-hour token expiration
- Disabled in development mode

## Security Headers

When enabled in production:

- **Content-Security-Policy**: Restricts resource loading
- **X-Frame-Options**: Prevents clickjacking
- **X-Content-Type-Options**: Prevents MIME sniffing
- **X-XSS-Protection**: Enables browser XSS filtering
- **Strict-Transport-Security**: Forces HTTPS (production only)
- **Referrer-Policy**: Controls referrer information

## Best Practices

1. **Never commit secrets**: JWT secrets should be environment variables
2. **Use HTTPS in production**: Security headers require HTTPS
3. **Regular security audits**: Review security configuration periodically
4. **Monitor rate limits**: Watch for abuse patterns
5. **Keep dependencies updated**: Security patches for Flask, etc.

## Testing Security

Run security tests:
```bash
python -m pytest tests/test_security.py
```

## Migration to Production

1. Set `PROD_MODE=true` environment variable
2. Set `JWT_SECRET` environment variable (strong random string)
3. Enable HTTPS (certificates required)
4. Configure Redis for rate limiting (optional but recommended)
5. Review and adjust rate limits as needed
6. Test authentication flow
7. Verify security headers are present

