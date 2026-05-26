# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of nqdev-geoip seriously. If you discover a security vulnerability, please follow these steps:

### 1. **Do Not** Disclose Publicly

Please do not open a public GitHub issue for security vulnerabilities. This helps protect users who haven't yet updated.

### 2. Report Privately

Send your report to: **quyit.job@gmail.com**

Include the following information:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if available)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity (see below)

### 4. Severity Levels

| Severity | Response Time | Examples |
|----------|---------------|----------|
| **Critical** | 24-48 hours | Remote code execution, authentication bypass |
| **High** | 3-7 days | SQL injection, XSS, privilege escalation |
| **Medium** | 14-30 days | Information disclosure, CSRF |
| **Low** | 30-90 days | Minor information leaks, non-exploitable bugs |

## Security Features

### 1. IP Banning System

The application includes an automated IP banning system that protects against malicious requests:

- **Automatic Detection**: Suspicious patterns are detected and IPs are automatically banned
- **Pattern Matching**: Blocks common attack vectors including:
  - WordPress/CMS scanning (`/wp-admin`, `/phpMyAdmin`)
  - Path traversal attacks (`../`, encoded variants)
  - PHP file scanning (`.php` files, vulnerable apps)
  - Configuration file access (`/.env`, `/.git`)
  - Common exploit endpoints (`/actuator`, `/console`, `/debug`)

**Configuration**: Patterns are defined in `dbs/suspicious.txt`

**Ban List**: Stored in `dbs/banned_ips.json` with timestamps and reasons

### 2. Admin Authentication

Admin endpoints require token-based authentication:

- **Token Validation**: All admin operations require `?token=<ADMIN_TOKEN>` parameter
- **Environment-Based**: Token is configured via `ADMIN_TOKEN` environment variable
- **Exempt from Ban Checks**: Admin endpoints are exempt from IP banning to prevent admin lockout

**Protected Endpoints**:
- `/geoip-update` - Database updates
- `/admin/ban/list` - View banned IPs
- `/admin/ban/add` - Ban an IP address
- `/admin/ban/unban` - Unban an IP address

### 3. Request Validation

Multiple layers of request validation:

- **HTTP Method Validation**: Only allows `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `OPTIONS`, `HEAD`
- **Invalid Character Detection**: Blocks requests with non-ASCII characters in JSON payloads
- **JSON Format Validation**: Validates JSON structure in POST/PUT/PATCH requests
- **IP Address Validation**: Validates IP format before processing

### 4. Reverse Proxy Support

The application uses `ProxyFix` middleware to safely handle reverse proxy headers:

- **X-Forwarded-For**: Properly extracts client IP behind proxies
- **X-Real-IP**: Fallback header for client IP detection
- **Trusted Proxy Headers**: Configured to work with Nginx/HAProxy

### 5. Private IP Handling

Special handling for private IP ranges:

- **CIDR Detection**: Identifies private IPs (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
- **Configurable Responses**: Custom responses for private IPs via `dbs/private_cidr_config.json`
- **Prevents Information Leakage**: Avoids exposing internal network topology

### 6. Logging and Monitoring

Comprehensive logging for security events:

- **Timed Rotation**: Daily log rotation with 7-day retention
- **Security Events Logged**:
  - Banned IP access attempts
  - Suspicious request patterns
  - Invalid HTTP methods
  - Invalid characters in payloads
  - Admin authentication failures
- **Log Location**: `logs/app_geoip_proxy_YYYYMMDD.log`

## Security Best Practices

### For Deployment

1. **Environment Variables**
   ```bash
   # Set strong, random values
   export SECRET_KEY="$(openssl rand -hex 32)"
   export ADMIN_TOKEN="$(openssl rand -hex 32)"
   ```

2. **File Permissions**
   ```bash
   # Restrict access to sensitive files
   chmod 600 config.py
   chmod 600 dbs/banned_ips.json
   chmod 700 dbs/
   ```

3. **Reverse Proxy Configuration**
   
   Use Nginx or HAProxy in front of the application:
   ```nginx
   # Nginx example
   location / {
       proxy_pass http://127.0.0.1:5000;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header Host $host;
   }
   ```

4. **HTTPS/TLS**
   
   Always use HTTPS in production:
   ```nginx
   server {
       listen 443 ssl http2;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       ssl_protocols TLSv1.2 TLSv1.3;
   }
   ```

5. **Docker Security**
   ```bash
   # Run as non-root user
   docker run --user 1000:1000 -p 5000:5000 nqdev-geoip
   
   # Limit resources
   docker run --memory="512m" --cpus="1.0" nqdev-geoip
   ```

### For Development

1. **Never Commit Secrets**
   - Use `.env` files (already in `.gitignore`)
   - Never hardcode tokens or keys
   - Use environment variables for all sensitive data

2. **Dependency Updates**
   ```bash
   # Regularly update dependencies
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

3. **Security Scanning**
   ```bash
   # Run security checks
   pip install safety bandit
   safety check
   bandit -r . -ll
   ```

4. **Code Review**
   - Review all changes to security-sensitive code
   - Pay special attention to:
     - Authentication/authorization logic
     - Input validation
     - File operations
     - Database queries

## Known Security Considerations

### 1. GeoIP Database Files

- **Public Data**: GeoIP databases contain public geolocation data
- **No Sensitive Information**: Databases do not contain personal or sensitive data
- **Regular Updates**: Databases are updated weekly via GitHub Actions

### 2. Admin Token in Query Parameters

**Current Implementation**: Admin token is passed as a query parameter (`?token=xxx`)

**Security Note**: Query parameters may be logged by web servers and proxies.

**Recommended Alternatives** (for future versions):
- Use HTTP headers: `Authorization: Bearer <token>`
- Use POST body for token transmission
- Implement session-based authentication

**Mitigation**:
- Use HTTPS to encrypt query parameters in transit
- Regularly rotate admin tokens
- Monitor access logs for unauthorized attempts

### 3. IP Spoofing

**Risk**: X-Forwarded-For headers can be spoofed if not behind a trusted proxy

**Mitigation**:
- Always deploy behind a reverse proxy (Nginx/HAProxy)
- Configure proxy to strip/override X-Forwarded-For from clients
- Use ProxyFix middleware (already implemented)

### 4. Rate Limiting

**Current Status**: No built-in rate limiting

**Recommendation**: Implement rate limiting at the reverse proxy level:
```nginx
# Nginx rate limiting example
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location / {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://127.0.0.1:5000;
}
```

## Security Checklist for Production

- [ ] Set strong `SECRET_KEY` and `ADMIN_TOKEN` environment variables
- [ ] Enable HTTPS/TLS with valid certificates
- [ ] Deploy behind a reverse proxy (Nginx/HAProxy)
- [ ] Configure rate limiting at proxy level
- [ ] Set proper file permissions (600 for config, 700 for dbs/)
- [ ] Enable firewall rules to restrict access
- [ ] Set up log monitoring and alerting
- [ ] Regularly update dependencies (`pip install --upgrade`)
- [ ] Review and update `dbs/suspicious.txt` patterns
- [ ] Backup `dbs/banned_ips.json` regularly
- [ ] Monitor `logs/` directory for security events
- [ ] Rotate admin tokens periodically
- [ ] Run security scans (safety, bandit)
- [ ] Review Docker container security settings

## Vulnerability Disclosure Policy

We follow responsible disclosure practices:

1. **Reporter Acknowledgment**: We will acknowledge receipt of your report within 48 hours
2. **Investigation**: We will investigate and validate the reported vulnerability
3. **Fix Development**: We will develop and test a fix
4. **Coordinated Disclosure**: We will coordinate the disclosure timeline with you
5. **Credit**: We will credit you in the security advisory (unless you prefer to remain anonymous)
6. **Public Disclosure**: After the fix is released, we will publish a security advisory

## Security Updates

Security updates are released as:
- **Patch versions** (1.0.x) for minor security fixes
- **Minor versions** (1.x.0) for moderate security improvements
- **Major versions** (x.0.0) for significant security overhauls

Subscribe to GitHub releases to receive notifications about security updates.

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/stable/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

## Contact

For security-related questions or concerns:
- **Email**: quyit.job@gmail.com
- **GitHub Issues**: For non-security bugs only
- **GitHub Security Advisories**: For coordinated disclosure

---

**Last Updated**: 2026-05-26

Thank you for helping keep nqdev-geoip secure!
