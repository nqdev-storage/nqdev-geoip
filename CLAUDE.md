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
# Development mode (Flask built-in server, debug enabled)
python geoip_proxy.py

# Production mode (Waitress WSGI server, recommended)
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

# Run single test function
pytest tests/test_ip_ban.py::test_ban_ip -v

# Linting (matches CI/CD checks)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### Docker

```bash
# Build image locally
docker build -t nqdev-geoip .

# Run container (maps port 8002 to container's 5000)
docker run -d -p 8002:5000 --name geoip nqdev-geoip

# Using Docker Compose (recommended for development)
docker-compose up -d
docker-compose logs -f geoip
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

**Note**: Docker Compose mounts `./dbs` and `./logs` as volumes for persistence.

## Architecture

### Application Entry Points

- **geoip_proxy.py** - Main Flask application with routes and middleware. Use for development with `debug=False`.
- **waitress_geoip_proxy.py** - Production WSGI server wrapper. Checks `__FLASK_ENV__` variable to determine if using Waitress (production) or Flask dev server.
- **config.py** - Configuration loaded via `app.config.from_object('config.Config')`. Reads `SECRET_KEY` and `ADMIN_TOKEN` from environment variables with fallback defaults.

### Request Flow

1. **ProxyFix Middleware** - Extracts real client IP from `X-Forwarded-For`/`X-Real-IP` headers (for reverse proxy deployments)
2. **@app.before_request Hook** - Security middleware that runs before all routes:
   - Exempts admin endpoints (`/admin/ban/*`) from IP ban checks
   - Checks if client IP is banned → returns 403
   - Validates HTTP method (GET/POST/PUT/DELETE/PATCH/OPTIONS/HEAD only)
   - Detects suspicious URL patterns → auto-bans IP and returns 403
   - Validates JSON payloads for invalid characters (non-ASCII) → auto-bans IP
3. **Route Handlers** - Process the request and return response
4. **Response** - Standardized via `utils/response_helper.py` for consistency

### Route Organization (Flask Blueprints)

- **routes/ip2location_routes.py** (`/ip2location/*`) - IP2Location database downloads
- **routes/user_routes.py** (`/user/*`) - User profile endpoints
- **routes/admin/ban_routes.py** (`/admin/ban/*`) - IP ban management (requires admin token)

Main routes defined directly in `geoip_proxy.py`:
- `/` - Welcome message
- `/geoip` - Country lookup using `GeoIP.dat`
- `/geoipcity` - City lookup using `GeoIPCity.dat`
- `/geoip-update` - Trigger database update (admin only)

### Security System

**IP Banning** (`utils/ip_ban.py`):
- Loads suspicious patterns from `dbs/suspicious.txt` at startup (regex patterns, case-insensitive)
- Maintains ban list in `dbs/banned_ips.json` with structure: `{"banned_ips": {"ip": {"reason": "...", "banned_at": "ISO8601"}}}`
- Auto-bans on: suspicious URL patterns, invalid characters in JSON, invalid HTTP methods
- Admin endpoints in `ADMIN_ENDPOINTS` list are exempt from ban checks to prevent lockout

**Private IP Handling** (`utils/private_cidr.py`):
- Checks if IP is in private CIDR ranges (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
- Returns configured default response from `dbs/private_cidr_config.json` if available
- Falls back to regular GeoIP lookup if no default configured
- Uses caching (`_config_cache`) to avoid repeated file I/O

### Database Files (`dbs/` directory)

**GeoIP Databases** (binary .dat files):
- `GeoIP.dat` - Country-level geolocation (loaded via `pygeoip.GeoIP()`)
- `GeoIPCity.dat` - City-level geolocation with lat/lon, region, postal code

**Security Configuration** (JSON/text files):
- `banned_ips.json` - Persistent ban list (read/write by `utils/ip_ban.py`)
- `suspicious.txt` - Regex patterns for auto-banning (one per line, `#` for comments)
- `private_cidr_config.json` - Default responses for private IPs

**Update Mechanism**: GitHub Actions workflow (`geoip_update.yml`) runs weekly, downloads from mailfud.org, extracts .gz files, commits to repo.

## Configuration

### Environment Variables

```bash
SECRET_KEY=your_secret_key_here        # Flask session secret (default: 'your_secret_key_here')
ADMIN_TOKEN=your_admin_token_here      # Admin API authentication (default: 'your_admin_token_here')
FLASK_APP=geoip_proxy.py               # Flask app entry point
FLASK_ENV=production                   # Environment mode
```

**Security Note**: Always set strong random values for `SECRET_KEY` and `ADMIN_TOKEN` in production:
```bash
export SECRET_KEY="$(openssl rand -hex 32)"
export ADMIN_TOKEN="$(openssl rand -hex 32)"
```

### Admin Authentication

Admin endpoints require `?token=<ADMIN_TOKEN>` query parameter. Token is validated by comparing against `Config.ADMIN_TOKEN` from environment.

**Protected Admin Endpoints**:
- `/geoip-update?token=<token>` - Trigger database update (currently commented out in code)
- `/admin/ban/list?token=<token>` - List all banned IPs
- `/admin/ban/add?token=<token>&ip=<ip>&reason=<reason>` - Ban an IP
- `/admin/ban/unban?token=<token>&ip=<ip>` - Remove IP from ban list

**Important**: Admin endpoints are in `ADMIN_ENDPOINTS` list and exempt from IP ban checks to prevent admin lockout.

## CI/CD Workflows

### GitHub Actions Workflows

- **geoip_update.yml** - Weekly database updates (Sundays at 00:00 UTC)
  - Downloads from mailfud.org: `GeoIP.dat.gz` and `GeoIPCity.dat.gz`
  - Extracts to `dbs/` directory
  - Commits with message: "Update GeoIP databases - vYYYY-MM-DD"
  - Requires `GH_TOKEN` secret for push permissions
  
- **python-app-testing.yml** - CI testing on push/PR to main
  - Runs on Python 3.13
  - Executes flake8 linting (same commands as local development)
  - Runs pytest test suite
  
- **docker-publish.yml** - Builds and publishes Docker images to GitHub Container Registry
  
- **changelog.yml** - Auto-generates CHANGELOG.md on releases

- **sync-wiki.yml** - Syncs documentation to GitHub Wiki

### Manual Database Update

The `geoip_update.py` module provides `download_and_extract(url, output_path)` function but is currently commented out in the `/geoip-update` endpoint. To enable:
1. Uncomment lines 167-168 in `geoip_proxy.py`
2. Ensure `logs/` directory exists for `app_geoip_update.log`

## API Endpoints

### Public Endpoints

- `GET /` - Welcome message
- `GET /geoip?ip=<ip>` - Country lookup
  - Returns: `{"country": "US"}` or `{"error": "IP address not found"}`
  - Checks private CIDR first, falls back to `GeoIP.dat` lookup
  
- `GET /geoipcity?ip=<ip>` - City lookup with full location data
  - Returns: `{"country_code": "US", "city": "Mountain View", "latitude": 37.386, "longitude": -122.0838, ...}`
  - Checks private CIDR first, falls back to `GeoIPCity.dat` lookup
  - Returns 400 for ValueError (invalid IP format)

### Admin Endpoints (require `?token=<ADMIN_TOKEN>`)

- `GET /geoip-update?token=<token>` - Trigger database update
  - Currently returns success without actually updating (lines 167-168 commented out)
  - Returns 101 if token missing, 200 on success
  
- `GET /admin/ban/list?token=<token>` - List all banned IPs
  - Returns: `{"banned_ips": {"1.2.3.4": {"reason": "...", "banned_at": "..."}}}`
  
- `POST /admin/ban/add?token=<token>&ip=<ip>&reason=<reason>` - Ban an IP
  - `reason` parameter is optional (defaults to "Manual ban by admin")
  
- `POST /admin/ban/unban?token=<token>&ip=<ip>` - Remove IP from ban list
  - Returns 404 if IP not in ban list

### Other Endpoints

- `GET /ip2location/download/<db_code>` - IP2Location database downloads (see `routes/ip2location_routes.py`)
- `GET /user/profile/<username>` - User profile lookup (see `routes/user_routes.py`)

### Error Responses

All endpoints return consistent error format:
- `{"error": "Access denied"}` - 403 (banned IP or suspicious request)
- `{"error": "Invalid HTTP method"}` - 405
- `{"error": "Missing IP address"}` - 400
- `{"error": "IP address not found"}` - 404
- `{"error": "Internal server error"}` - 500

## Important Implementation Details

### IP Banning System

**Pattern Loading**: Suspicious patterns are loaded from `dbs/suspicious.txt` at module import time (not per-request). To add new patterns:
1. Edit `dbs/suspicious.txt` (one regex pattern per line, case-insensitive)
2. Restart the application to reload patterns

**Common Patterns Blocked**:
- WordPress/CMS: `/wp-admin`, `/phpMyAdmin`, `/wp-login`
- Path traversal: `../`, `..%2F`, `%2E%2E%2F`
- Config files: `/.env`, `/.git`, `/config.php`
- PHP scanning: `\.php$`, `\.php\?`, `/shell.php`
- Exploit endpoints: `/actuator`, `/console`, `/debug`

**Ban List Management**:
- Stored in `dbs/banned_ips.json` with structure: `{"banned_ips": {"ip": {"reason": "...", "banned_at": "ISO8601"}}}`
- Auto-bans are logged with reason like "Suspicious request: /wp-admin"
- Manual bans via admin API include custom reason
- No automatic unban - must be done manually via admin API

**Admin Endpoint Exemption**: The list `ADMIN_ENDPOINTS = ['/admin/ban/list', '/admin/ban/add', '/admin/ban/unban']` in `routes/admin/ban_routes.py` is checked in the `@app.before_request` hook to prevent admin lockout.

### Private IP Handling

**CIDR Detection**: Uses Python's `ipaddress` module to check if IP is in configured CIDR ranges from `dbs/private_cidr_config.json`.

**Configuration Format**:
```json
{
  "private_cidrs": ["10.0.0.0/8", "192.168.0.0/16", "172.16.0.0/12"],
  "default_response": {
    "country_code": "US",
    "city": "Private Network",
    ...
  }
}
```

**Behavior**:
- `/geoip` endpoint: Returns `country_code` from default_response if configured, otherwise falls back to GeoIP lookup
- `/geoipcity` endpoint: Returns full `default_response` object if configured, otherwise falls back to GeoIPCity lookup
- Config is cached in memory (`_config_cache`) and reloaded only if file mtime changes

### Logging

**Log Files**:
- `logs/app_geoip_proxy_YYYYMMDD.log` - Main application logs (created at startup)
- `logs/app_geoip_update.log` - Database update logs (if update feature enabled)

**Rotation**: Uses `TimedRotatingFileHandler` with:
- `when="midnight"` - Rotates at midnight
- `interval=1` - Daily rotation
- `backupCount=7` - Keeps 7 days of logs

**Security Events Logged**:
- Banned IP access attempts (WARNING level)
- Suspicious requests detected (WARNING level)
- Invalid HTTP methods (WARNING level)
- Invalid characters in payloads (WARNING level)
- Exceptions (ERROR level with traceback)

### ProxyFix Middleware

The application uses `ProxyFix(app.wsgi_app)` to handle reverse proxy headers. This means:
- `request.remote_addr` will contain the real client IP (not the proxy IP)
- `X-Forwarded-For` and `X-Real-IP` headers are trusted
- **Deploy behind a trusted reverse proxy** (Nginx/HAProxy) that strips client-provided X-Forwarded-For headers

### GeoIP Database Loading

Databases are loaded at module level (startup):
```python
geoip = pygeoip.GeoIP('./dbs/GeoIP.dat')
GeoIPCity = pygeoip.GeoIP('./dbs/GeoIPCity.dat')
```

**Important**: If databases are updated while the app is running, you must restart the application to reload them. The weekly GitHub Actions workflow commits new databases but doesn't trigger a restart - handle this in your deployment.

## Testing Considerations

### Test Structure

- **tests/test_geoip_proxy.py** - Main application endpoint tests
- **tests/test_ip_ban.py** - IP banning system unit tests
- **tests/test_private_cidr.py** - Private CIDR detection tests

### Testing Requirements

- Tests use pytest framework
- GeoIP database files (`dbs/GeoIP.dat`, `dbs/GeoIPCity.dat`) must exist for integration tests
- `dbs/banned_ips.json` file access required for ban functionality tests
- Admin token validation tests should use the token from `Config.ADMIN_TOKEN`

### Running Tests in CI

The `python-app-testing.yml` workflow runs on Python 3.13 and executes:
1. Flake8 linting (syntax errors and undefined names)
2. Full pytest suite

**Note**: If tests fail locally but pass in CI (or vice versa), check Python version differences (local may use 3.11, CI uses 3.13).

## Deployment Notes

### Docker Deployment

**Container Configuration** (from `docker-compose.yml`):
- Image: `ghcr.io/nqdev-storage/nqdev-geoip:latest`
- Port mapping: `8002:5000` (host:container)
- Volumes mounted:
  - `./dbs:/app/dbs` - Persistent database files
  - `./logs:/app/logs` - Persistent log files
- Resource limits: 1 CPU, 1GB RAM max
- Timezone: `Asia/Ho_Chi_Minh`

**Important**: Volume mounts allow database updates from GitHub Actions to persist into running containers, but you must restart the container to reload databases into memory.

### Production Checklist

1. Set strong `SECRET_KEY` and `ADMIN_TOKEN` environment variables
2. Deploy behind reverse proxy (Nginx/HAProxy) with proper X-Forwarded-For handling
3. Enable HTTPS/TLS at reverse proxy level
4. Configure rate limiting at reverse proxy (no built-in rate limiting)
5. Set up log monitoring for security events (grep for "WARNING" in logs)
6. Ensure `dbs/` directory has proper permissions (writable for updates)
7. Set up automated container restart after database updates (weekly on Sundays)

### Reverse Proxy Example (Nginx)

```nginx
location / {
    proxy_pass http://127.0.0.1:8002;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header Host $host;
    
    # Rate limiting
    limit_req zone=api burst=20 nodelay;
}
```

## Python Version

- **Development**: Python 3.11+ recommended
- **CI/CD**: Python 3.13 (GitHub Actions)
- **Docker**: Python 3.11.2-alpine3.16
- **Compatibility**: Code should work on Python 3.11-3.13

## Additional Resources

- **Wiki Documentation**: See `docs/wiki/` directory for detailed guides
- **Security Policy**: See `SECURITY.md` for vulnerability reporting and security features
- **Changelog**: See `CHANGELOG.md` for version history
- **API Documentation**: Swagger UI available at `/apidocs/` when server is running
