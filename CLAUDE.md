# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**nqdev-geoip** is a Flask-based REST API service that provides free IP geolocation lookups using GeoIP Legacy and GeoLite2 databases. The service includes automatic database updates via CI/CD, IP banning for security, and Docker deployment support.

## Development Commands

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Development mode (Flask built-in server)
python geoip_proxy.py

# Production mode (Waitress WSGI server)
python waitress_geoip_proxy.py
```

Server runs on `http://localhost:5000` with Swagger docs at `http://localhost:5000/apidocs/`

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_geoip_proxy.py
pytest tests/test_ip_ban.py
pytest tests/test_private_cidr.py

# Run with verbose output
pytest -v

# Run linting
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### Docker

```bash
# Build image
docker build -t nqdev-geoip .

# Run container
docker run -d -p 5000:5000 --name geoip nqdev-geoip

# Using Docker Compose
docker-compose up -d
docker-compose logs -f geoip
docker-compose down
```

## Architecture

### Core Application Structure

- **geoip_proxy.py** - Main Flask application with route definitions and middleware
- **waitress_geoip_proxy.py** - Production WSGI server entry point using Waitress
- **config.py** - Application configuration (SECRET_KEY, ADMIN_TOKEN)
- **geoip_update.py** - Database download and update utilities

### Route Blueprints

Routes are organized into Flask blueprints in the `routes/` directory:

- **routes/ip2location_routes.py** - IP2Location database download endpoints
- **routes/user_routes.py** - User profile endpoints
- **routes/admin/ban_routes.py** - Admin IP ban management endpoints

### Utility Modules

- **utils/ip_ban.py** - IP banning system with suspicious request detection
  - Maintains banned IPs in `dbs/banned_ips.json`
  - Loads suspicious patterns from `dbs/suspicious.txt`
  - Auto-bans IPs making suspicious requests (path traversal, PHP scanning, etc.)
- **utils/private_cidr.py** - Private IP range detection and default responses
- **utils/response_helper.py** - Standardized API response formatting

### Security Middleware

The `@app.before_request` middleware in `geoip_proxy.py` performs:
1. IP ban checking (except for admin endpoints)
2. HTTP method validation
3. Suspicious request pattern detection
4. Invalid character detection in request bodies

Admin endpoints in `ADMIN_ENDPOINTS` are exempt from ban checks to prevent admin lockout.

### Database Files

Located in `dbs/` directory:
- **GeoIP.dat** - GeoIP Legacy country database
- **GeoIPCity.dat** - GeoIP Legacy city database
- **banned_ips.json** - Banned IP list with reasons and timestamps
- **suspicious.txt** - Suspicious URL patterns for auto-banning
- **private_cidr_config.json** - Configuration for private IP responses

Databases are automatically updated weekly via GitHub Actions workflow.

## Configuration

### Environment Variables

```bash
SECRET_KEY=your_secret_key_here        # Flask session secret
ADMIN_TOKEN=your_admin_token_here      # Admin API authentication token
FLASK_APP=geoip_proxy.py
FLASK_ENV=production
```

### Admin Token Usage

Admin endpoints require `?token=<ADMIN_TOKEN>` query parameter:
- `/geoip-update` - Update GeoIP databases
- `/admin/ban/list` - List banned IPs
- `/admin/ban/add` - Ban an IP
- `/admin/ban/unban` - Unban an IP

## CI/CD Workflows

### GitHub Actions

- **geoip_update.yml** - Weekly database updates (Sundays at 00:00 UTC)
- **python-app-testing.yml** - Run tests and linting on push/PR
- **docker-publish.yml** - Build and publish Docker images
- **changelog.yml** - Auto-generate CHANGELOG.md on releases

### Database Update Process

The `geoip_update.yml` workflow:
1. Downloads latest databases from mailfud.org
2. Extracts .gz files to `dbs/` directory
3. Commits changes with version tag (YYYY-MM-DD)
4. Pushes to main branch

## API Endpoints

### Public Endpoints

- `GET /` - Welcome message
- `GET /geoip?ip=<ip>` - Country lookup (returns `{"country": "US"}`)
- `GET /geoipcity?ip=<ip>` - City lookup (returns full location data)

### Admin Endpoints (require token)

- `GET /geoip-update?token=<token>` - Update databases
- `GET /admin/ban/list?token=<token>` - List banned IPs
- `POST /admin/ban/add?token=<token>&ip=<ip>&reason=<reason>` - Ban IP
- `POST /admin/ban/unban?token=<token>&ip=<ip>` - Unban IP

### IP2Location Endpoints

- `GET /ip2location/download/<db_code>` - Download IP2Location database

### User Endpoints

- `GET /user/profile/<username>` - Get user profile

## Important Notes

### IP Banning System

- Suspicious patterns are loaded from `dbs/suspicious.txt` at startup
- Patterns include: WordPress admin, phpMyAdmin, path traversal, PHP file scanning
- Banned IPs receive `403 Forbidden` with `{"error": "Access denied"}`
- Admin endpoints are exempt from ban checks

### Private IP Handling

- Private IPs (10.x.x.x, 192.168.x.x, 172.16-31.x.x) can return configured defaults
- Configuration in `dbs/private_cidr_config.json`
- Falls back to regular lookup if no default configured

### Logging

- Logs stored in `logs/` directory
- Rotated daily with 7-day retention
- Format: `app_geoip_proxy_YYYYMMDD.log`
- Blocked requests logged with IP, path, and reason

### ProxyFix Middleware

The app uses `ProxyFix` middleware to handle reverse proxy headers (X-Forwarded-For, X-Real-IP) when deployed behind Nginx/HAProxy.

## Testing Considerations

- Tests use pytest framework
- Mock GeoIP database files may be needed for testing
- Admin token validation should be tested
- IP ban functionality requires `dbs/banned_ips.json` file access

## Python Version

- Primary: Python 3.11+
- CI/CD uses: Python 3.13
- Docker image: Python 3.11.2-alpine3.16
