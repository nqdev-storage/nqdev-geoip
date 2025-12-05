# ⚙️ Cấu hình

Hướng dẫn cấu hình các thành phần của **nqdev-geoip**.

## 📝 Tổng quan

Cấu hình được quản lý qua:
1. **Biến môi trường** - Ưu tiên cao nhất
2. **File `config.py`** - Cấu hình mặc định
3. **File JSON trong `dbs/`** - Cấu hình runtime

## 🔐 Cấu hình bảo mật

### config.py

```python
import os

class Config:
    # Secret key cho Flask sessions
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    
    # Token xác thực cho API admin
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'your_admin_token_here')
    
    # SQLAlchemy (nếu sử dụng)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Debug mode (tắt trong production)
    DEBUG = False
```

### Biến môi trường

```bash
# Thiết lập trong shell
export SECRET_KEY="your_secure_secret_key"
export ADMIN_TOKEN="your_secure_admin_token"

# Hoặc trong docker-compose.yml
environment:
  - SECRET_KEY=your_secure_secret_key
  - ADMIN_TOKEN=your_secure_admin_token
```

### Tạo secret key an toàn

```python
# Sử dụng Python để tạo secret key
import secrets
print(secrets.token_hex(32))
# Output: a1b2c3d4e5f6...
```

```bash
# Hoặc dùng command line
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🌐 Cấu hình Private CIDR

Cho phép trả về response mặc định cho các IP trong dải private (10.x.x.x, 192.168.x.x, v.v.).

### File: `dbs/private_cidr.json`

```json
{
  "enabled": true,
  "default_country_code": "VN",
  "default_response": {
    "city": "Private Network",
    "region_code": "",
    "area_code": 0,
    "time_zone": "Asia/Ho_Chi_Minh",
    "dma_code": 0,
    "metro_code": null,
    "country_code3": "VNM",
    "latitude": 21.0285,
    "postal_code": "",
    "longitude": 105.8542,
    "country_code": "VN",
    "country_name": "Vietnam",
    "continent": "AS"
  }
}
```

### Các tùy chọn

| Tùy chọn | Kiểu | Mô tả |
|----------|------|-------|
| `enabled` | boolean | Bật/tắt tính năng |
| `default_country_code` | string | Mã quốc gia trả về cho endpoint `/geoip` |
| `default_response` | object | Response đầy đủ cho endpoint `/geoipcity` |

### Private CIDR ranges được hỗ trợ

- `10.0.0.0/8` - Class A private
- `172.16.0.0/12` - Class B private
- `192.168.0.0/16` - Class C private
- `127.0.0.0/8` - Loopback
- `169.254.0.0/16` - Link-local

## 🚫 Cấu hình IP Ban

### File: `dbs/banned_ips.json`

```json
{
  "banned_ips": {
    "192.168.1.100": {
      "reason": "Suspicious request: /wp-admin",
      "banned_at": "2025-12-05T10:30:00"
    },
    "10.0.0.50": {
      "reason": "Manual ban by admin",
      "banned_at": "2025-12-04T15:45:00"
    }
  }
}
```

File này được tạo và cập nhật tự động khi:
- Phát hiện request đáng ngờ
- Admin sử dụng API `/admin/ban/add`

### Xóa ban thủ công

1. Sử dụng API: `POST /admin/ban/unban?token=xxx&ip=192.168.1.100`
2. Hoặc sửa trực tiếp file `banned_ips.json`

## 🔍 Cấu hình Suspicious Patterns

### File: `dbs/suspicious.txt`

Danh sách các pattern URL đáng ngờ (mỗi dòng một pattern regex):

```text
# WordPress attacks
/wp-admin
/wp-login
/wp-content
/wp-includes
/xmlrpc\.php

# Admin panels
/phpMyAdmin
/phpmyadmin
/adminer
/pma

# Path traversal
\.\.\/
\.\.%2[fF]
/etc/passwd
/etc/shadow

# PHP scanning
\.php$
\.php\?

# CMS scanning
/joomla
/drupal
/magento
/typo3

# Other attacks
/\.env
/\.git
/config\.php
/shell\.php
/cgi-bin
/solr
/actuator
/console
```

### Cú pháp

- Mỗi dòng là một regex pattern
- Dòng bắt đầu bằng `#` là comment
- Dòng trống được bỏ qua
- Pattern được match case-insensitive

### Thêm pattern mới

```bash
# Thêm vào file
echo "/new-attack-path" >> dbs/suspicious.txt

# Restart server để áp dụng
docker-compose restart
```

## 📊 Cấu hình Logging

### Trong `geoip_proxy.py`

```python
import logging
from logging.handlers import TimedRotatingFileHandler

# Cấu hình logger
logging.basicConfig(
    level=logging.DEBUG,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        TimedRotatingFileHandler(
            filename="logs/app_geoip_proxy.log",
            when="midnight",      # Rotate hàng ngày
            interval=1,
            backupCount=7,        # Giữ 7 file log cũ
            encoding='utf-8',
        )
    ]
)
```

### Các level logging

| Level | Giá trị | Mô tả |
|-------|---------|-------|
| DEBUG | 10 | Thông tin chi tiết (development) |
| INFO | 20 | Thông tin chung |
| WARNING | 30 | Cảnh báo |
| ERROR | 40 | Lỗi |
| CRITICAL | 50 | Lỗi nghiêm trọng |

### Thay đổi log level

```python
# Trong code
logging.getLogger().setLevel(logging.INFO)

# Hoặc qua biến môi trường
export LOG_LEVEL=INFO
```

## 🐳 Cấu hình Docker

### docker-compose.yml resources

```yaml
deploy:
  resources:
    limits:
      cpus: "1"        # Tối đa 1 CPU core
      memory: "1G"     # Tối đa 1GB RAM
    reservations:
      cpus: "0.25"     # Đảm bảo ít nhất 25% CPU
      memory: "256M"   # Đảm bảo ít nhất 256MB RAM
```

### Logging trong Docker

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "100MB"   # Kích thước tối đa mỗi file log
    max-file: "3"       # Số file log tối đa
```

### Timezone

```yaml
environment:
  - TZ=Asia/Ho_Chi_Minh
```

Danh sách timezone: [Wikipedia - List of tz database time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

## 🔧 Cấu hình Flask

### Environment variables

```bash
# Flask application
export FLASK_APP=geoip_proxy.py

# Environment mode
export FLASK_ENV=production  # hoặc development

# Debug mode (chỉ development)
export FLASK_DEBUG=0  # 0 = off, 1 = on
```

### Custom config class

```python
# config.py
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
```

Sử dụng:
```python
# geoip_proxy.py
app.config.from_object('config.ProductionConfig')
```

## 📁 Cấu hình Database Paths

### Đường dẫn mặc định

```python
# GeoIP Legacy
GeoIP_path = './dbs/GeoIP.dat'
GeoIPCity_path = './dbs/GeoIPCity.dat'

# Ban list
BAN_LIST_FILE = './dbs/banned_ips.json'

# Suspicious patterns
SUSPICIOUS_PATTERNS_FILE = './dbs/suspicious.txt'

# Private CIDR
PRIVATE_CIDR_FILE = './dbs/private_cidr.json'
```

### Thay đổi đường dẫn

```bash
# Qua biến môi trường (nếu được hỗ trợ)
export GEOIP_DB_PATH=/custom/path/GeoIP.dat
export GEOIP_CITY_DB_PATH=/custom/path/GeoIPCity.dat
```

## ⚡ Cấu hình Production

### Waitress (Windows/Cross-platform)

```python
# waitress_geoip_proxy.py
from waitress import serve
from geoip_proxy import app

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000, threads=4)
```

### Gunicorn (Linux/Unix)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 geoip_proxy:app
```

### Cấu hình Gunicorn

```python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
threads = 2
worker_class = "sync"
timeout = 30
keepalive = 2
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

## 📋 Tóm tắt file cấu hình

| File | Vị trí | Mô tả |
|------|--------|-------|
| `config.py` | Root | Cấu hình Flask chính |
| `docker-compose.yml` | Root | Docker Compose config |
| `Dockerfile` | Root | Docker build config |
| `requirements.txt` | Root | Python dependencies |
| `private_cidr.json` | `dbs/` | Private CIDR settings |
| `banned_ips.json` | `dbs/` | IP ban list |
| `suspicious.txt` | `dbs/` | Suspicious URL patterns |

---

➡️ **Tiếp theo**: [Quản trị](Admin-Guide) - Hướng dẫn quản trị hệ thống
