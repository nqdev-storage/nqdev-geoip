# 📦 Hướng dẫn Cài đặt

Trang này hướng dẫn chi tiết cách cài đặt và thiết lập **nqdev-geoip**.

## 📋 Yêu cầu hệ thống

### Phần mềm cần thiết

| Phần mềm | Phiên bản | Ghi chú |
|----------|-----------|---------|
| Python | 3.11+ | Khuyến nghị Python 3.11 hoặc 3.13 |
| pip | Mới nhất | Python package manager |
| Git | 2.x+ | Version control |
| Docker | 20.x+ | (Tùy chọn) Cho Docker deployment |

### Hệ điều hành hỗ trợ

- ✅ Linux (Ubuntu, CentOS, Debian, Alpine)
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Docker containers

## 🔧 Cài đặt từ Source Code

### Bước 1: Clone Repository

```bash
git clone https://github.com/nqdev-storage/nqdev-geoip.git
cd nqdev-geoip
```

### Bước 2: Tạo môi trường ảo Python

**Linux/macOS:**
```bash
# Cài đặt virtualenv (nếu chưa có)
pip install virtualenv

# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường
source venv/bin/activate
```

**Windows:**
```powershell
# Cài đặt virtualenv (nếu chưa có)
pip install virtualenv

# Tạo môi trường ảo
# Lưu ý: Thay đường dẫn Python phù hợp với máy của bạn
python -m venv venv
# Hoặc với đường dẫn cụ thể: virtualenv venv -p "C:\Python311\python.exe"

# Kích hoạt môi trường
.\venv\Scripts\activate
```

### Bước 3: Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

**Danh sách các package chính:**
- `Flask` - Web framework
- `flasgger` - Swagger documentation
- `pygeoip` - GeoIP lookup library
- `waitress` - Production WSGI server
- `gunicorn` - Unix WSGI server
- `requests` - HTTP library
- `pytest` - Testing framework

### Bước 4: Kiểm tra Database

Đảm bảo thư mục `dbs/` chứa các file database cần thiết:

```
dbs/
├── GeoIP.dat       # GeoIP Legacy Country database
└── GeoIPCity.dat   # GeoIP Legacy City database
```

Nếu database chưa có hoặc cần cập nhật, xem phần [Cập nhật Database](#-cập-nhật-database).

### Bước 5: Chạy Server

**Development mode:**
```bash
python geoip_proxy.py
```

**Production mode (với Waitress):**
```bash
python waitress_geoip_proxy.py
```

Server sẽ chạy tại: `http://localhost:5000`

## 🐳 Cài đặt bằng Docker

### Sử dụng Docker Image có sẵn

```bash
# Pull image từ GitHub Container Registry
docker pull ghcr.io/nqdev-storage/nqdev-geoip:latest

# Chạy container
docker run -d \
  --name geoip \
  -p 5000:5000 \
  -v $(pwd)/dbs:/app/dbs \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/nqdev-storage/nqdev-geoip:latest
```

### Build Docker Image từ Source

```bash
# Build image
docker build -t nqdev-geoip .

# Chạy container
docker run -d \
  --name geoip \
  -p 5000:5000 \
  nqdev-geoip
```

### Sử dụng Docker Compose

```bash
# Khởi động service
docker-compose up -d

# Xem logs
docker-compose logs -f geoip

# Dừng service
docker-compose down
```

**docker-compose.yml configuration:**
```yaml
services:
  geoip:
    image: ghcr.io/nqdev-storage/nqdev-geoip:latest
    container_name: geoip
    restart: unless-stopped
    ports:
      - 8002:5000
    volumes:
      - ./dbs:/app/dbs
      - ./logs:/app/logs
    environment:
      - TZ=Asia/Ho_Chi_Minh
      - PYTHONUNBUFFERED=1
```

## 📥 Cập nhật Database

### Tải GeoIP Legacy Database

Database được cập nhật tự động qua CI/CD workflow. Để cập nhật thủ công:

**Nguồn chính (mailfud.org):**
```bash
# GeoIP Country
wget -O dbs/GeoIP.dat.gz https://mailfud.org/geoip-legacy/GeoIP.dat.gz
gunzip -f dbs/GeoIP.dat.gz

# GeoIP City
wget -O dbs/GeoIPCity.dat.gz https://mailfud.org/geoip-legacy/GeoIPCity.dat.gz
gunzip -f dbs/GeoIPCity.dat.gz
```

### Tải GeoLite2 Database (tùy chọn)

```bash
# GeoLite2 Country
wget -O dbs/GeoLite2-Country.mmdb https://git.io/GeoLite2-Country.mmdb

# GeoLite2 City
wget -O dbs/GeoLite2-City.mmdb https://git.io/GeoLite2-City.mmdb

# GeoLite2 ASN
wget -O dbs/GeoLite2-ASN.mmdb https://git.io/GeoLite2-ASN.mmdb
```

**Mirror thay thế:**
- [P3TERX/GeoLite.mmdb](https://github.com/P3TERX/GeoLite.mmdb)

## ✅ Kiểm tra Cài đặt

### Kiểm tra server đang chạy

```bash
curl http://localhost:5000/
# Expected: "Welcome to Flask!"
```

### Kiểm tra API GeoIP

```bash
# Test Country lookup
curl "http://localhost:5000/geoip?ip=8.8.8.8"
# Expected: {"country":"US"}

# Test City lookup  
curl "http://localhost:5000/geoipcity?ip=8.8.8.8"
# Expected: {"city":"...", "country_code":"US", ...}
```

### Truy cập Swagger API Documentation

Mở trình duyệt và truy cập: `http://localhost:5000/apidocs/`

## 🧪 Chạy Tests

```bash
# Chạy tất cả tests
pytest

# Chạy test cụ thể
pytest test_geoip_proxy.py
pytest tests/test_ip_ban.py

# Chạy test với verbose output
pytest -v
```

## 🔧 Cấu hình môi trường

### Biến môi trường

```bash
# Secret key cho Flask sessions
export SECRET_KEY="your_secret_key_here"

# Admin token cho các API quản trị
export ADMIN_TOKEN="your_admin_token_here"

# Flask environment
export FLASK_APP=geoip_proxy.py
export FLASK_ENV=production
```

### File cấu hình

Xem `config.py` để tùy chỉnh:

```python
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'your_admin_token_here')
    DEBUG = False
```

## ❓ Xử lý sự cố cài đặt

### Lỗi "No module named 'pygeoip'"

```bash
pip install pygeoip
```

### Lỗi "Database file not found"

Đảm bảo file `dbs/GeoIP.dat` và `dbs/GeoIPCity.dat` tồn tại. Xem phần [Cập nhật Database](#-cập-nhật-database).

### Lỗi "Port 5000 already in use"

```bash
# Tìm process đang dùng port 5000
lsof -i :5000

# Hoặc chạy trên port khác
python geoip_proxy.py --port 8000
```

### Lỗi permission khi ghi logs

```bash
# Tạo thư mục logs với quyền phù hợp
mkdir -p logs
chmod 755 logs
```

---

➡️ **Tiếp theo**: [API Reference](API-Reference) - Tài liệu API đầy đủ
