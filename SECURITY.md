# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it privately:

**Email**: [Add security contact email]

**Do NOT**:
- Open a public GitHub issue
- Disclose publicly before a fix is available

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 1 week
- **Fix timeline**: Depends on severity

## Scope

Security issues we care about:
- Authentication bypass
- Data exposure
- XSS/CSRF vulnerabilities
- Encryption weaknesses (especially in KIM)
- Injection attacks

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x     | ✅ Yes    |
| 1.x     | ❌ No     |

## Security Best Practices

This project follows:
- HTTPS in production
- Password hashing (bcrypt)
- Input validation and sanitization
- Rate limiting
- CSRF protection
- Environment variables for secrets
