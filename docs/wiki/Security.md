# 🔐 Bảo mật

Tài liệu về các tính năng bảo mật và best practices của **nqdev-geoip**.

## 🛡️ Tổng quan bảo mật

**nqdev-geoip** được thiết kế với nhiều lớp bảo mật để chống lại các cuộc tấn công phổ biến:

- ✅ IP Banning System (tự động và thủ công)
- ✅ Suspicious Request Detection (54+ patterns)
- ✅ Token-based Admin Authentication
- ✅ HTTP Method Validation
- ✅ Invalid Character Detection
- ✅ Proxy Header Handling (X-Forwarded-For)
- ✅ Admin Endpoint Protection
- ✅ Comprehensive Logging

## 🚫 Hệ thống IP Banning

### Cơ chế hoạt động

1. **Automatic Banning**: Tự động ban IP khi phát hiện request đáng ngờ
2. **Manual Banning**: Admin có thể ban IP thủ công qua API
3. **Persistent Storage**: Ban list lưu trong `dbs/banned_ips.json`
4. **Middleware Check**: Kiểm tra mỗi request trước khi xử lý

### Ban List Structure

```json
{
  "banned_ips": {
    "192.168.1.100": {
      "reason": "Suspicious request: /wp-admin",
      "banned_at": "2026-05-26T10:30:00"
    },
    "10.0.0.50": {
      "reason": "Manual ban by admin",
      "banned_at": "2026-05-25T15:45:00"
    }
  }
}
```

### Automatic Ban Triggers

IP sẽ bị ban tự động khi:

1. **Suspicious URL Patterns**: Truy cập các URL đáng ngờ
2. **Invalid HTTP Methods**: Sử dụng method không hợp lệ
3. **Invalid Characters**: Request body chứa ký tự lạ (non-ASCII)

### Admin Endpoint Exemption

Các endpoint admin được miễn kiểm tra ban để tránh khóa admin:

```python
ADMIN_ENDPOINTS = [
    '/admin/ban/list',
    '/admin/ban/add', 
    '/admin/ban/unban'
]
```

**Lý do**: Nếu admin bị ban nhầm, họ vẫn có thể truy cập admin API để tự unban.

## 🔍 Suspicious Request Detection

### Pattern Categories

#### 1. WordPress Attacks
```
/wp-admin
/wp-login
/wp-content
/wp-includes
/xmlrpc.php
```

#### 2. Admin Panel Scanning
```
/phpMyAdmin
/phpmyadmin
/adminer
/pma
/cpanel
/plesk
```

#### 3. Path Traversal
```
../                    # Plain path traversal
..%2F                  # URL encoded ../
%2E%2E%2F             # Double URL encoded
/etc/passwd           # Direct access
/etc/shadow
```

#### 4. PHP File Scanning
```
\.php$                # Any .php file
\.php\?               # PHP with query string
/shell\.php
/config\.php
```

#### 5. CMS Scanning
```
/joomla
/drupal
/magento
/typo3
/roundcube
/webmail
```

#### 6. Config & Sensitive Files
```
/\.env
/\.git
/config\.php
/\.htaccess
```

#### 7. Exploit Scanning
```
/cgi-bin
/solr
/actuator
/console
/debug
/trace
/api/v1/pods
```

### Pattern Matching

- **Case-insensitive**: Patterns match không phân biệt hoa thường
- **Regex-based**: Sử dụng Python regex
- **Pre-compiled**: Patterns được compile một lần khi khởi động
- **Fast matching**: Kiểm tra nhanh với compiled patterns

### Custom Patterns

Thêm patterns tùy chỉnh vào `dbs/suspicious.txt`:

```bash
# Custom patterns
/my-admin-panel
/secret-endpoint
/internal-api
```

**Lưu ý**: Restart server sau khi thêm patterns mới.

## 🔑 Token Authentication

### Admin Token

**Cấu hình**:
```python
# config.py
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'your_admin_token_here')
```

**Sử dụng**:
```bash
curl "http://localhost:5000/admin/ban/list?token=YOUR_ADMIN_TOKEN"
```

### Token Validation

```python
def validate_admin_token(token: str) -> bool:
    expected_token = Config.ADMIN_TOKEN
    return token == expected_token
```

### Best Practices

1. **Không dùng token mặc định**: Luôn thay đổi trong production
2. **Sử dụng token mạnh**: Ít nhất 32 ký tự random
3. **Lưu trong environment**: Không hardcode trong code
4. **Rotate định kỳ**: Thay đổi token định kỳ
5. **HTTPS only**: Chỉ sử dụng qua HTTPS trong production

### Tạo Token An Toàn

```python
import secrets

# Tạo token 32 bytes (64 hex characters)
token = secrets.token_hex(32)
print(token)
# Output: a1b2c3d4e5f6...
```

```bash
# Hoặc dùng command line
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🌐 Proxy Header Handling

### ProxyFix Middleware

```python
from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(app.wsgi_app)
```

**Chức năng**:
- Xử lý `X-Forwarded-For` header
- Xử lý `X-Real-IP` header
- Lấy đúng client IP khi đứng sau reverse proxy

### Get Client IP

```python
def get_client_ip(request) -> str:
    # ProxyFix đã xử lý X-Forwarded-For
    if request.remote_addr:
        return request.remote_addr
    
    # Fallback to headers
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip.strip()
    
    return 'unknown'
```

### Reverse Proxy Configuration

**Nginx**:
```nginx
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 🔒 HTTP Method Validation

### Valid Methods

```python
VALID_HTTP_METHODS = [
    'GET', 
    'POST', 
    'PUT', 
    'DELETE', 
    'PATCH', 
    'OPTIONS', 
    'HEAD'
]
```

### Validation Logic

```python
def is_valid_http_method(request) -> bool:
    return request.method in VALID_HTTP_METHODS
```

**Auto-ban**: IP sẽ bị ban nếu sử dụng method không hợp lệ.

## 🛡️ Input Validation

### Invalid Character Detection

```python
def contains_invalid_chars(data: str) -> bool:
    """Kiểm tra ký tự lạ không phải ASCII"""
    return bool(re.search(r'[^\x00-\x7F]+', data))
```

**Mục đích**: Phát hiện các cuộc tấn công injection với ký tự đặc biệt.

### IP Address Validation

```python
import ipaddress

def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
```

## 📊 Security Logging

### Log Events

**Banned IP Access**:
```
2026-05-26 10:30:00 - WARNING - Blocked request from banned IP: 192.168.1.100 - /geoip
```

**Suspicious Request Detected**:
```
2026-05-26 10:30:00 - WARNING - Suspicious request detected from IP: 192.168.1.100 - /wp-admin
```

**IP Banned**:
```
2026-05-26 10:30:00 - WARNING - IP 192.168.1.100 banned. Reason: Suspicious request: /wp-admin
```

**IP Unbanned**:
```
2026-05-26 10:35:00 - INFO - IP 192.168.1.100 unbanned.
```

### Log Analysis

**Tìm các IP bị ban nhiều nhất**:
```bash
grep "banned" logs/*.log | cut -d' ' -f5 | sort | uniq -c | sort -rn | head -10
```

**Tìm các path đáng ngờ phổ biến**:
```bash
grep "Suspicious request" logs/*.log | grep -oP "(?<=: ).+" | sort | uniq -c | sort -rn | head -10
```

**Tìm các IP cố gắng truy cập sau khi bị ban**:
```bash
grep "Blocked request from banned IP" logs/*.log | cut -d' ' -f7 | sort | uniq -c | sort -rn
```

## 🚨 Attack Scenarios & Mitigations

### 1. WordPress Scanning Attack

**Attack**:
```bash
curl http://target.com/wp-admin
curl http://target.com/wp-login.php
curl http://target.com/xmlrpc.php
```

**Mitigation**:
- ✅ Automatic ban on first suspicious request
- ✅ Pattern matching detects WordPress paths
- ✅ Logged for analysis

### 2. Path Traversal Attack

**Attack**:
```bash
curl http://target.com/../../etc/passwd
curl http://target.com/%2e%2e%2f%2e%2e%2fetc%2fpasswd
```

**Mitigation**:
- ✅ Pattern matching detects `../` and encoded variants
- ✅ Automatic ban
- ✅ Logged with full path

### 3. SQL Injection Attempt

**Attack**:
```bash
curl "http://target.com/geoip?ip=1.1.1.1' OR '1'='1"
```

**Mitigation**:
- ✅ IP validation rejects invalid format
- ✅ pygeoip library handles input safely
- ✅ No SQL database used (file-based)

### 4. DDoS Attack

**Attack**:
```bash
# Flood requests from multiple IPs
for i in {1..1000}; do
    curl http://target.com/geoip?ip=8.8.8.8 &
done
```

**Mitigation**:
- ✅ Reverse proxy rate limiting (Nginx)
- ✅ IP banning for excessive requests
- ✅ Lightweight response (minimal processing)
- ⚠️ Consider: Cloudflare/CDN for large-scale DDoS

### 5. Admin API Brute Force

**Attack**:
```bash
# Try multiple tokens
for token in $(cat wordlist.txt); do
    curl "http://target.com/admin/ban/list?token=$token"
done
```

**Mitigation**:
- ✅ Strong token requirement (32+ chars)
- ✅ Rate limiting at reverse proxy
- ✅ Failed attempts logged
- ⚠️ Consider: Account lockout after N failed attempts

### 6. Header Injection

**Attack**:
```bash
curl -H "X-Forwarded-For: 127.0.0.1" http://target.com/admin/ban/list?token=xxx
```

**Mitigation**:
- ✅ ProxyFix middleware handles headers correctly
- ✅ Trusted proxy configuration
- ✅ Admin endpoints still require valid token

## 🔐 Security Best Practices

### 1. Token Management

```bash
# ❌ BAD: Hardcoded token
ADMIN_TOKEN = "admin123"

# ✅ GOOD: Environment variable
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')

# ✅ GOOD: Strong random token
ADMIN_TOKEN = "a1b2c3d4e5f6789...64chars"
```

### 2. HTTPS Only

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name geoip.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name geoip.yourdomain.com;
    
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    
    # Strong SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
}
```

### 3. Rate Limiting

```nginx
# Limit to 10 requests/second per IP
limit_req_zone $binary_remote_addr zone=geoip:10m rate=10r/s;

location / {
    limit_req zone=geoip burst=20 nodelay;
    proxy_pass http://127.0.0.1:5000;
}
```

### 4. IP Whitelist for Admin

```nginx
# Only allow admin access from internal IPs
location /admin {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    proxy_pass http://127.0.0.1:5000;
}
```

### 5. Regular Updates

```bash
# Update GeoIP databases weekly (automated via CI/CD)
# Update Docker image regularly
docker pull ghcr.io/nqdev-storage/nqdev-geoip:latest
docker-compose up -d

# Update Python dependencies
pip install --upgrade -r requirements.txt
```

### 6. Monitoring & Alerting

```bash
# Monitor ban rate
BAN_COUNT=$(python -c "
import json
with open('dbs/banned_ips.json', 'r') as f:
    data = json.load(f)
    print(len(data.get('banned_ips', {})))
")

if [ "$BAN_COUNT" -gt 100 ]; then
    echo "⚠️ High number of banned IPs: $BAN_COUNT"
    # Send alert...
fi
```

### 7. Backup & Recovery

```bash
# Backup ban list and configs
tar -czf backup_security_$(date +%Y%m%d).tar.gz \
    dbs/banned_ips.json \
    dbs/suspicious.txt \
    dbs/private_cidr_config.json

# Restore if needed
tar -xzf backup_security_20260526.tar.gz
docker-compose restart
```

## 🔍 Security Audit Checklist

- [ ] Admin token đã được thay đổi từ mặc định
- [ ] Token có độ dài ít nhất 32 ký tự
- [ ] HTTPS được bật trong production
- [ ] Rate limiting được cấu hình tại reverse proxy
- [ ] Admin endpoints chỉ accessible từ IPs nội bộ
- [ ] Logs được monitor định kỳ
- [ ] Ban list được review định kỳ
- [ ] Suspicious patterns được cập nhật
- [ ] Docker image được update định kỳ
- [ ] Backup được thực hiện định kỳ
- [ ] SSL certificate còn hạn (>30 days)
- [ ] Firewall rules được cấu hình đúng

## 📋 Security Headers (Nginx)

```nginx
# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

## 🚨 Incident Response

### Khi phát hiện tấn công

1. **Identify**: Xác định nguồn tấn công qua logs
2. **Contain**: Ban IP ngay lập tức
3. **Analyze**: Phân tích pattern tấn công
4. **Mitigate**: Thêm pattern mới vào suspicious.txt
5. **Document**: Ghi lại incident và response
6. **Review**: Review và cải thiện security measures

### Emergency Commands

```bash
# Ban IP ngay lập tức
curl -X POST "http://localhost:5000/admin/ban/add?token=TOKEN&ip=ATTACKER_IP&reason=Attack"

# Xem top attacking IPs
grep "$(date +%Y-%m-%d)" logs/*.log | cut -d' ' -f5 | sort | uniq -c | sort -rn | head -20

# Block at firewall level
iptables -A INPUT -s ATTACKER_IP -j DROP

# Restart service if needed
docker-compose restart
```

---

➡️ **Tiếp theo**: [Admin Guide](Admin-Guide) - Hướng dẫn quản trị hệ thống
