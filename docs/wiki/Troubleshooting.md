# 🔧 Xử lý sự cố

Hướng dẫn giải quyết các vấn đề thường gặp khi sử dụng **nqdev-geoip**.

## 🚨 Các vấn đề phổ biến

### 1. Server không khởi động

#### Triệu chứng
- Container không start
- Lỗi khi chạy `python geoip_proxy.py`

#### Nguyên nhân và giải pháp

**a. Thiếu dependencies:**
```bash
# Kiểm tra
pip list

# Cài đặt lại
pip install -r requirements.txt
```

**b. Database không tìm thấy:**
```bash
# Kiểm tra file
ls -la dbs/GeoIP.dat dbs/GeoIPCity.dat

# Nếu thiếu, download lại
wget -O dbs/GeoIP.dat.gz https://mailfud.org/geoip-legacy/GeoIP.dat.gz
gunzip -f dbs/GeoIP.dat.gz

wget -O dbs/GeoIPCity.dat.gz https://mailfud.org/geoip-legacy/GeoIPCity.dat.gz
gunzip -f dbs/GeoIPCity.dat.gz
```

**c. Port đã được sử dụng:**
```bash
# Kiểm tra port 5000
lsof -i :5000

# Kill process đang dùng
kill <PID>

# Hoặc đổi port
python geoip_proxy.py --port 8000
```

**d. Lỗi quyền truy cập:**
```bash
# Tạo thư mục logs
mkdir -p logs
chmod 755 logs

# Kiểm tra quyền database
chmod 644 dbs/*.dat
```

---

### 2. API trả về 403 Forbidden

#### Triệu chứng
```json
{"error": "Access denied"}
```

#### Nguyên nhân
IP của bạn đã bị ban do:
- Request tới URL đáng ngờ
- Bị admin ban thủ công

#### Giải pháp

**a. Kiểm tra IP có bị ban:**
```bash
curl "http://localhost:5000/admin/ban/list?token=YOUR_ADMIN_TOKEN"
```

**b. Xóa ban cho IP:**
```bash
curl -X POST "http://localhost:5000/admin/ban/unban?token=YOUR_ADMIN_TOKEN&ip=YOUR_IP"
```

**c. Xóa trực tiếp từ file:**
```bash
# Xem ban list
cat dbs/banned_ips.json

# Sửa file (xóa IP cần unban)
nano dbs/banned_ips.json

# Hoặc xóa tất cả
echo '{"banned_ips": {}}' > dbs/banned_ips.json
```

---

### 3. API trả về 404 Not Found

#### Triệu chứng
```json
{"error": "IP address not found"}
```

#### Nguyên nhân
- IP không có trong database GeoIP
- Database quá cũ
- IP là private/reserved

#### Giải pháp

**a. Kiểm tra IP:**
```bash
# Thử với IP public khác
curl "http://localhost:5000/geoip?ip=8.8.8.8"
```

**b. Cập nhật database:**
```bash
wget -O dbs/GeoIP.dat.gz https://mailfud.org/geoip-legacy/GeoIP.dat.gz
gunzip -f dbs/GeoIP.dat.gz
docker-compose restart
```

**c. Cấu hình Private CIDR (cho IP private):**

Tạo file `dbs/private_cidr.json`:
```json
{
  "enabled": true,
  "default_country_code": "VN",
  "default_response": {
    "city": "Private Network",
    "country_code": "VN",
    "country_name": "Vietnam"
  }
}
```

---

### 4. API trả về 400 Bad Request

#### Triệu chứng
```json
{"error": "Missing IP address"}
```
hoặc
```json
{"error": "Invalid value provided"}
```

#### Nguyên nhân
- Thiếu parameter `ip`
- IP format không hợp lệ

#### Giải pháp

**a. Kiểm tra request:**
```bash
# Đúng
curl "http://localhost:5000/geoip?ip=8.8.8.8"

# Sai - thiếu ip
curl "http://localhost:5000/geoip"

# Sai - ip không hợp lệ
curl "http://localhost:5000/geoip?ip=invalid"
```

**b. Validate IP trước khi gọi API:**
```python
import ipaddress

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
```

---

### 5. API trả về 500 Internal Server Error

#### Triệu chứng
```json
{"error": "Internal server error"}
```

#### Nguyên nhân
- Database corrupt
- Lỗi code
- Thiếu memory

#### Giải pháp

**a. Xem logs chi tiết:**
```bash
# Docker
docker logs --tail 100 geoip

# File
tail -100 logs/app_geoip_proxy_*.log
```

**b. Tải lại database:**
```bash
rm dbs/GeoIP.dat dbs/GeoIPCity.dat
wget -O dbs/GeoIP.dat.gz https://mailfud.org/geoip-legacy/GeoIP.dat.gz
wget -O dbs/GeoIPCity.dat.gz https://mailfud.org/geoip-legacy/GeoIPCity.dat.gz
gunzip -f dbs/*.gz
docker-compose restart
```

**c. Kiểm tra memory:**
```bash
# Docker
docker stats geoip

# Tăng memory limit
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: "2G"
```

---

### 6. Container Docker không start

#### Triệu chứng
```bash
docker-compose up
# Container exits immediately
```

#### Giải pháp

**a. Xem logs:**
```bash
docker-compose logs geoip
```

**b. Kiểm tra volumes:**
```bash
# Đảm bảo thư mục tồn tại
mkdir -p dbs logs

# Kiểm tra quyền
ls -la dbs/ logs/
```

**c. Build lại image:**
```bash
docker-compose build --no-cache
docker-compose up -d
```

**d. Chạy interactive để debug:**
```bash
docker run -it --rm ghcr.io/nqdev-storage/nqdev-geoip:latest /bin/sh
```

---

### 7. Swagger UI không hoạt động

#### Triệu chứng
- Truy cập `/apidocs/` trả về lỗi
- Swagger không load

#### Giải pháp

**a. Kiểm tra flasgger:**
```bash
pip install flasgger --upgrade
```

**b. Kiểm tra server đang chạy:**
```bash
curl http://localhost:5000/
# Should return "Welcome to Flask!"
```

**c. Clear browser cache:**
- Ctrl+Shift+R (hard refresh)
- Hoặc mở incognito window

---

### 8. Admin token không hoạt động

#### Triệu chứng
```json
{"isSuccess": false, "message": "Invalid or missing token"}
```

#### Giải pháp

**a. Kiểm tra token:**
```bash
# Xem token trong config
grep ADMIN_TOKEN config.py

# Hoặc environment
echo $ADMIN_TOKEN
```

**b. Đặt lại token:**
```bash
# Environment
export ADMIN_TOKEN="new_token_here"

# Hoặc docker-compose.yml
environment:
  - ADMIN_TOKEN=new_token_here

# Restart
docker-compose restart
```

---

### 9. Logs không được ghi

#### Triệu chứng
- Thư mục logs trống
- File log không cập nhật

#### Giải pháp

**a. Kiểm tra quyền:**
```bash
chmod 755 logs/
```

**b. Kiểm tra mount volume (Docker):**
```yaml
# docker-compose.yml
volumes:
  - ./logs:/app/logs
```

**c. Tạo thư mục logs trong container:**
```bash
docker exec geoip mkdir -p /app/logs
docker-compose restart
```

---

### 10. Performance chậm

#### Triệu chứng
- Response time cao (>1s)
- Timeout errors

#### Giải pháp

**a. Kiểm tra resources:**
```bash
docker stats geoip
```

**b. Tăng workers:**
```python
# waitress_geoip_proxy.py
serve(app, host='0.0.0.0', port=5000, threads=8)
```

**c. Kiểm tra database size:**
```bash
ls -lh dbs/*.dat
```

**d. Sử dụng reverse proxy với caching:**
```nginx
proxy_cache_path /tmp/nginx_cache levels=1:2 keys_zone=geoip_cache:10m max_size=100m inactive=60m;

location /geoip {
    proxy_cache geoip_cache;
    proxy_cache_valid 200 60m;
    proxy_pass http://127.0.0.1:5000;
}
```

---

## 🛠️ Công cụ Debug

### Kiểm tra health

```bash
# Server running
curl -f http://localhost:5000/ || echo "Server down"

# GeoIP working
curl -f "http://localhost:5000/geoip?ip=8.8.8.8" || echo "GeoIP error"

# Admin API
curl -f "http://localhost:5000/admin/ban/list?token=TOKEN" || echo "Admin error"
```

### Script kiểm tra toàn diện

```bash
#!/bin/bash

echo "=== Health Check ==="

# 1. Server
if curl -sf http://localhost:5000/ > /dev/null; then
    echo "✅ Server: OK"
else
    echo "❌ Server: FAILED"
fi

# 2. GeoIP Country
if curl -sf "http://localhost:5000/geoip?ip=8.8.8.8" | grep -q "country"; then
    echo "✅ GeoIP Country: OK"
else
    echo "❌ GeoIP Country: FAILED"
fi

# 3. GeoIP City
if curl -sf "http://localhost:5000/geoipcity?ip=8.8.8.8" | grep -q "country_code"; then
    echo "✅ GeoIP City: OK"
else
    echo "❌ GeoIP City: FAILED"
fi

# 4. Database files
if [ -f dbs/GeoIP.dat ] && [ -f dbs/GeoIPCity.dat ]; then
    echo "✅ Database files: OK"
else
    echo "❌ Database files: MISSING"
fi

# 5. Logs directory
if [ -d logs ] && [ -w logs ]; then
    echo "✅ Logs directory: OK"
else
    echo "❌ Logs directory: ISSUE"
fi
```

### Debug Python

```python
# Chạy Python interactive
python

>>> import pygeoip
>>> geoip = pygeoip.GeoIP('./dbs/GeoIP.dat')
>>> geoip.country_code_by_addr('8.8.8.8')
'US'
>>> 
>>> city = pygeoip.GeoIP('./dbs/GeoIPCity.dat')
>>> city.record_by_addr('8.8.8.8')
{'city': '...', 'country_code': 'US', ...}
```

---

## 📞 Hỗ trợ

Nếu không thể giải quyết vấn đề:

1. **Kiểm tra Issues**: [GitHub Issues](https://github.com/nqdev-storage/nqdev-geoip/issues)
2. **Tạo Issue mới** với thông tin:
   - Mô tả chi tiết vấn đề
   - Logs liên quan
   - Phiên bản đang sử dụng
   - Môi trường (OS, Docker version, etc.)
3. **Liên hệ**: quyit.job@gmail.com

---

⬅️ **Quay lại**: [Home](Home) - Trang chủ Wiki
