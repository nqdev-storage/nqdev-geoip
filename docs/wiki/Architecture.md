# 🏗️ Kiến trúc hệ thống

Tài liệu mô tả kiến trúc và thiết kế của **nqdev-geoip**.

## 📐 Tổng quan kiến trúc

**nqdev-geoip** được xây dựng theo mô hình **Flask Blueprint Architecture** với các thành phần được tách biệt rõ ràng.

```
┌─────────────────────────────────────────────────────────┐
│                    Client (HTTP/HTTPS)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Reverse Proxy (Nginx/Traefik)              │
│                  - SSL Termination                       │
│                  - Rate Limiting                         │
│                  - Load Balancing                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Flask Application                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Middleware Layer                          │  │
│  │  - ProxyFix (X-Forwarded-For handling)          │  │
│  │  - IP Ban Check (@app.before_request)           │  │
│  │  - Suspicious Request Detection                  │  │
│  │  - HTTP Method Validation                        │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                   │
│                      ▼                                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Route Blueprints                     │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │  GeoIP Routes (geoip_proxy.py)             │ │  │
│  │  │  - GET /                                    │ │  │
│  │  │  - GET /geoip                               │ │  │
│  │  │  - GET /geoipcity                           │ │  │
│  │  │  - GET /geoip-update                        │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │  Admin Routes (routes/admin/ban_routes.py) │ │  │
│  │  │  - GET /admin/ban/list                      │ │  │
│  │  │  - POST /admin/ban/add                      │ │  │
│  │  │  - POST /admin/ban/unban                    │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │  User Routes (routes/user_routes.py)       │ │  │
│  │  │  - GET /user/profile/<username>            │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │  IP2Location Routes                         │ │  │
│  │  │  - GET /ip2location/download/<db_code>     │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                   │
│                      ▼                                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Utility Modules                      │  │
│  │  - utils/ip_ban.py                               │  │
│  │  - utils/private_cidr.py                         │  │
│  │  - utils/response_helper.py                      │  │
│  └───────────────────┬───────────────────────────────┘  │
│                      │                                   │
│                      ▼                                   │
│  ┌───────────────────────────────────────────────────┐  │
│  │           GeoIP Database Layer                    │  │
│  │  - pygeoip.GeoIP (GeoIP.dat)                     │  │
│  │  - pygeoip.GeoIP (GeoIPCity.dat)                 │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Data Storage Layer                      │
│  - dbs/GeoIP.dat (Country database)                     │
│  - dbs/GeoIPCity.dat (City database)                    │
│  - dbs/banned_ips.json (Ban list)                       │
│  - dbs/suspicious.txt (Suspicious patterns)             │
│  - dbs/private_cidr_config.json (Private CIDR config)   │
│  - logs/ (Application logs)                             │
└─────────────────────────────────────────────────────────┘
```

## 🧩 Các thành phần chính

### 1. Flask Application Core

**File**: `geoip_proxy.py`

Ứng dụng Flask chính với các chức năng:
- Khởi tạo Flask app và Swagger documentation
- Đăng ký các blueprints
- Cấu hình logging với TimedRotatingFileHandler
- Load GeoIP databases (GeoIP.dat, GeoIPCity.dat)
- Middleware xử lý proxy headers (ProxyFix)

```python
app = Flask(__name__)
app.config.from_object('config.Config')
Swagger(app=app)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Load GeoIP databases
geoip = pygeoip.GeoIP('./dbs/GeoIP.dat')
GeoIPCity = pygeoip.GeoIP('./dbs/GeoIPCity.dat')
```

### 2. Middleware Layer

**Middleware**: `@app.before_request`

Xử lý trước mỗi request:
1. **IP Ban Check**: Kiểm tra IP có trong ban list không
2. **Admin Endpoint Exemption**: Miễn kiểm tra cho admin endpoints
3. **HTTP Method Validation**: Chỉ cho phép các method hợp lệ
4. **Suspicious Request Detection**: Phát hiện request đáng ngờ
5. **Invalid Character Detection**: Phát hiện ký tự lạ trong request body
6. **Auto-ban**: Tự động ban IP nếu phát hiện request đáng ngờ

```python
@app.before_request
def check_banned_ip():
    if request.path in ADMIN_ENDPOINTS:
        return None
    
    client_ip = get_client_ip(request)
    
    if is_ip_banned(client_ip):
        return jsonify({"error": "Access denied"}), 403
    
    if not is_valid_http_method(request):
        ban_ip(client_ip, f"Invalid HTTP method: {request.method}")
        return jsonify({"error": "Access denied"}), 403
    
    if is_suspicious_request(request.path):
        ban_ip(client_ip, f"Suspicious request: {request.path}")
        return jsonify({"error": "Access denied"}), 403
```

### 3. Route Blueprints

#### a. GeoIP Routes (Main)

**File**: `geoip_proxy.py`

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/` | GET | Welcome message |
| `/geoip` | GET | Country lookup |
| `/geoipcity` | GET | City lookup |
| `/geoip-update` | GET | Update databases (admin) |

#### b. Admin Routes

**File**: `routes/admin/ban_routes.py`

Blueprint: `admin_ban_bp` (prefix: `/admin/ban`)

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/admin/ban/list` | GET | List banned IPs |
| `/admin/ban/add` | POST | Ban an IP |
| `/admin/ban/unban` | POST | Unban an IP |

**Security**: Tất cả endpoints yêu cầu `token` parameter để xác thực.

#### c. User Routes

**File**: `routes/user_routes.py`

Blueprint: `user_bp` (prefix: `/user`)

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/user/profile/<username>` | GET | Get user profile |

#### d. IP2Location Routes

**File**: `routes/ip2location_routes.py`

Blueprint: `ip2location_bp` (prefix: `/ip2location`)

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/ip2location/download/<db_code>` | GET | Download IP2Location database |

### 4. Utility Modules

#### a. IP Ban Module

**File**: `utils/ip_ban.py`

**Chức năng**:
- Load/save ban list từ `dbs/banned_ips.json`
- Load suspicious patterns từ `dbs/suspicious.txt`
- Kiểm tra IP có bị ban không
- Ban/unban IP
- Phát hiện request đáng ngờ bằng regex patterns
- Lấy client IP từ proxy headers

**Key Functions**:
```python
is_ip_banned(ip: str) -> bool
ban_ip(ip: str, reason: str) -> bool
unban_ip(ip: str) -> bool
is_suspicious_request(path: str) -> bool
get_client_ip(request) -> str
```

**Suspicious Patterns**: 54+ patterns bao gồm:
- WordPress attacks: `/wp-admin`, `/wp-login`, `/xmlrpc.php`
- Admin panels: `/phpMyAdmin`, `/adminer`
- Path traversal: `../`, `%2e%2e/`, `/etc/passwd`
- PHP scanning: `.php$`, `.php?`
- CMS scanning: `/joomla`, `/drupal`, `/magento`
- Config files: `/.env`, `/.git`

#### b. Private CIDR Module

**File**: `utils/private_cidr.py`

**Chức năng**:
- Kiểm tra IP có thuộc private CIDR không
- Trả về response mặc định cho private IPs
- Cache configuration để tối ưu performance

**Private CIDR Ranges**:
- `10.0.0.0/8` - Class A private
- `172.16.0.0/12` - Class B private
- `192.168.0.0/16` - Class C private

**Key Functions**:
```python
is_private_cidr(ip: str) -> bool
get_private_cidr_response() -> Optional[Dict]
get_private_cidr_country_code() -> Optional[str]
```

#### c. Response Helper Module

**File**: `utils/response_helper.py`

**Chức năng**:
- Chuẩn hóa response format
- Hỗ trợ success/error responses

**Key Functions**:
```python
okResult(isSuccess, message, payload={}, error='', http_code=-1)
errorResult(success, message, status_code=400)
```

### 5. Configuration

**File**: `config.py`

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'your_admin_token_here')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
```

**Environment Variables**:
- `SECRET_KEY`: Flask session secret
- `ADMIN_TOKEN`: Admin API authentication
- `FLASK_APP`: Application entry point
- `FLASK_ENV`: Environment mode (production/development)

### 6. Database Layer

#### GeoIP Databases

**GeoIP.dat** (Country Database):
- Size: ~3.4MB
- Format: GeoIP Legacy binary
- Update: Weekly via CI/CD
- Source: https://mailfud.org/geoip-legacy/

**GeoIPCity.dat** (City Database):
- Size: ~24.3MB
- Format: GeoIP Legacy binary
- Update: Weekly via CI/CD
- Source: https://mailfud.org/geoip-legacy/

#### Configuration Files

**banned_ips.json**:
```json
{
  "banned_ips": {
    "192.168.1.100": {
      "reason": "Suspicious request: /wp-admin",
      "banned_at": "2026-05-26T10:30:00"
    }
  }
}
```

**suspicious.txt**:
- 54+ regex patterns
- One pattern per line
- Comments start with `#`
- Case-insensitive matching

**private_cidr_config.json**:
```json
{
  "private_cidrs": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
  "default_response": {
    "country_code": "VN",
    "country_name": "Vietnam",
    ...
  }
}
```

## 🔄 Request Flow

### 1. Normal GeoIP Lookup Request

```
Client Request
    ↓
Reverse Proxy (Nginx)
    ↓
ProxyFix Middleware (handle X-Forwarded-For)
    ↓
@app.before_request
    ├─ Get client IP
    ├─ Check if IP banned → [403 if banned]
    ├─ Validate HTTP method → [403 if invalid]
    ├─ Check suspicious patterns → [403 + auto-ban if suspicious]
    └─ Check invalid characters → [403 + auto-ban if found]
    ↓
Route Handler (/geoip or /geoipcity)
    ├─ Validate IP parameter → [400 if missing/invalid]
    ├─ Check if private CIDR → [return default if configured]
    ├─ Lookup in GeoIP database
    └─ Return result → [200 if found, 404 if not found]
    ↓
Response to Client
```

### 2. Admin Ban Request

```
Client Request (with token)
    ↓
@app.before_request
    └─ Skip ban check (admin endpoint exemption)
    ↓
Admin Route Handler
    ├─ Validate admin token → [401 if invalid]
    ├─ Validate parameters → [400 if missing]
    ├─ Perform action (list/ban/unban)
    └─ Return result → [200 if success]
    ↓
Response to Client
```

### 3. Suspicious Request (Auto-ban)

```
Client Request (e.g., /wp-admin)
    ↓
@app.before_request
    ├─ Get client IP
    ├─ Check suspicious patterns → [MATCH]
    ├─ Ban IP automatically
    ├─ Log warning
    └─ Return 403 Forbidden
    ↓
Response: {"error": "Access denied"}
```

## 🔐 Security Architecture

### Defense Layers

1. **Network Layer**: Reverse proxy rate limiting
2. **Application Layer**: IP ban system
3. **Pattern Detection**: Suspicious request detection
4. **Admin Protection**: Token-based authentication
5. **Logging**: Comprehensive audit trail

### Security Features

- **IP Banning**: Automatic and manual
- **Pattern Matching**: 54+ suspicious patterns
- **Admin Exemption**: Admin endpoints không bị ban check
- **Token Authentication**: Secure admin access
- **Proxy Trust**: ProxyFix middleware handles X-Forwarded-For
- **HTTP Method Validation**: Only allow valid methods
- **Invalid Character Detection**: Detect non-ASCII characters

## 📊 Data Flow

### Database Update Flow

```
GitHub Actions (Weekly Cron)
    ↓
Download GeoIP.dat.gz & GeoIPCity.dat.gz
    ↓
Extract .gz files
    ↓
Commit to dbs/ directory
    ↓
Push to main branch
    ↓
Docker image rebuild (auto-trigger)
    ↓
Deploy new image
```

### Logging Flow

```
Application Event
    ↓
Python logging module
    ↓
TimedRotatingFileHandler
    ├─ Console output (StreamHandler)
    └─ File output (logs/app_geoip_proxy_YYYYMMDD.log)
        ├─ Rotate at midnight
        ├─ Keep 7 days
        └─ UTF-8 encoding
```

## 🚀 Deployment Architecture

### Docker Deployment

```
Docker Host
    ↓
Docker Container (Alpine Linux + Python 3.11)
    ├─ Waitress WSGI Server (production)
    ├─ Flask Application
    ├─ Volume: ./dbs → /app/dbs
    ├─ Volume: ./logs → /app/logs
    └─ Port: 5000 (internal) → 8002 (external)
```

### Production Stack

```
Internet
    ↓
Cloudflare/CDN (optional)
    ↓
Nginx (Reverse Proxy + SSL)
    ├─ Rate Limiting
    ├─ SSL Termination
    └─ Load Balancing
    ↓
Docker Container (nqdev-geoip)
    ├─ Waitress WSGI Server
    └─ Flask Application
    ↓
GeoIP Databases (local files)
```

## 📈 Performance Considerations

### Optimization Strategies

1. **Database Caching**: GeoIP databases loaded once at startup
2. **Config Caching**: Private CIDR config cached with mtime check
3. **Pattern Compilation**: Regex patterns compiled once at startup
4. **WSGI Server**: Waitress with multiple threads
5. **Reverse Proxy Caching**: Nginx can cache responses

### Scalability

- **Horizontal Scaling**: Multiple containers behind load balancer
- **Vertical Scaling**: Increase threads in Waitress
- **Database Replication**: Shared volume for databases
- **Stateless Design**: No session state, easy to scale

## 🔗 Integration Points

### External Dependencies

- **mailfud.org**: GeoIP database source
- **GitHub Actions**: CI/CD automation
- **Docker Hub/GHCR**: Container registry

### API Clients

- **HTTP Clients**: curl, requests, fetch
- **Reverse Proxies**: Nginx, Traefik, HAProxy
- **Monitoring**: Prometheus, Grafana (via custom exporters)

---

➡️ **Tiếp theo**: [API Reference](API-Reference) - Tài liệu API đầy đủ
