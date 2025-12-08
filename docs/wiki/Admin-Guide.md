# 🛡️ Hướng dẫn Quản trị

Tài liệu hướng dẫn quản trị và vận hành **nqdev-geoip**.

## 👤 Tổng quan Admin

### Admin Token

Admin token được sử dụng để xác thực các API quản trị. Token được cấu hình trong:

```python
# config.py
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN', 'your_admin_token_here')
```

**⚠️ Quan trọng**: Luôn thay đổi token mặc định trong môi trường production!

### Admin Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/admin/ban/list` | GET | Liệt kê IP bị ban |
| `/admin/ban/add` | POST | Thêm IP vào ban list |
| `/admin/ban/unban` | POST | Xóa IP khỏi ban list |

## 🚫 Quản lý IP Ban

### Xem danh sách IP bị ban

```bash
curl "http://localhost:5000/admin/ban/list?token=YOUR_ADMIN_TOKEN"
```

**Response:**
```json
{
  "isSuccess": true,
  "message": "Ban list retrieved",
  "payload": {
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

### Thêm IP vào ban list

```bash
# Ban với lý do mặc định
curl -X POST "http://localhost:5000/admin/ban/add?token=YOUR_ADMIN_TOKEN&ip=192.168.1.100"

# Ban với lý do cụ thể
curl -X POST "http://localhost:5000/admin/ban/add?token=YOUR_ADMIN_TOKEN&ip=192.168.1.100&reason=Spam%20attack"
```

### Xóa IP khỏi ban list

```bash
curl -X POST "http://localhost:5000/admin/ban/unban?token=YOUR_ADMIN_TOKEN&ip=192.168.1.100"
```

### Quản lý trực tiếp file

Ban list được lưu tại `dbs/banned_ips.json`:

```json
{
  "banned_ips": {
    "192.168.1.100": {
      "reason": "Spam attack",
      "banned_at": "2025-12-05T10:30:00"
    }
  }
}
```

**Xóa tất cả ban:**
```bash
echo '{"banned_ips": {}}' > dbs/banned_ips.json
```

## 🔍 Quản lý Suspicious Patterns

### Xem patterns hiện tại

```bash
cat dbs/suspicious.txt
```

### Thêm pattern mới

```bash
# Thêm một pattern
echo "/new-attack-path" >> dbs/suspicious.txt

# Thêm nhiều patterns
cat >> dbs/suspicious.txt << EOF
/attack-path-1
/attack-path-2
/malicious\.php
EOF
```

### Xóa pattern

```bash
# Sửa trực tiếp file
nano dbs/suspicious.txt

# Hoặc dùng sed
sed -i '/pattern-to-remove/d' dbs/suspicious.txt
```

### Patterns mặc định

Nếu file `suspicious.txt` không tồn tại, hệ thống sử dụng patterns mặc định:

- WordPress: `/wp-admin`, `/wp-login`, `/wp-content`, `/xmlrpc.php`
- Admin panels: `/phpMyAdmin`, `/adminer`, `/pma`
- Path traversal: `../`, `%2e%2e/`, `/etc/passwd`
- PHP scanning: `.php$`, `.php?`
- CMS: `/joomla`, `/drupal`, `/magento`
- Config files: `/.env`, `/.git`, `/config.php`

## 📊 Monitoring & Logs

### Xem logs

**Docker:**
```bash
# Real-time logs
docker logs -f geoip

# Logs với timestamps
docker logs --timestamps geoip

# 100 dòng cuối
docker logs --tail 100 geoip
```

**Trực tiếp từ file:**
```bash
# Xem logs mới nhất
tail -f logs/app_geoip_proxy_*.log

# Tìm kiếm trong logs
grep "banned" logs/app_geoip_proxy_*.log
grep "Suspicious" logs/app_geoip_proxy_*.log
```

### Phân tích logs

**Tìm các IP bị ban nhiều nhất:**
```bash
grep "banned" logs/*.log | cut -d' ' -f5 | sort | uniq -c | sort -rn | head -10
```

**Tìm các path đáng ngờ phổ biến:**
```bash
grep "Suspicious request" logs/*.log | grep -oP "(?<=: ).+" | sort | uniq -c | sort -rn | head -10
```

### Log format

```
2025-12-05 10:30:00 - WARNING - Suspicious request detected from IP: 192.168.1.100 - /wp-admin
2025-12-05 10:30:00 - WARNING - IP 192.168.1.100 banned. Reason: Suspicious request: /wp-admin
2025-12-05 10:31:00 - WARNING - Blocked request from banned IP: 192.168.1.100 - /geoip
```

### Metrics cần theo dõi

| Metric | Mô tả | Cách kiểm tra |
|--------|-------|---------------|
| Request rate | Số request/phút | `grep "$(date +%Y-%m-%d)" logs/*.log \| wc -l` |
| Ban rate | Số IP bị ban/giờ | `grep "banned" logs/*.log \| wc -l` |
| Error rate | Số lỗi | `grep "ERROR" logs/*.log \| wc -l` |
| Response time | Thời gian phản hồi | Xem logs Nginx/reverse proxy |

## 🔄 Cập nhật Database

### Tự động (CI/CD)

Database được cập nhật tự động hàng tuần qua GitHub Actions workflow.

### Thủ công

```bash
# Download GeoIP Legacy (sử dụng HTTPS nếu có)
wget -O dbs/GeoIP.dat.gz https://mailfud.org/geoip-legacy/GeoIP.dat.gz
gunzip -f dbs/GeoIP.dat.gz

wget -O dbs/GeoIPCity.dat.gz https://mailfud.org/geoip-legacy/GeoIPCity.dat.gz
gunzip -f dbs/GeoIPCity.dat.gz

# Restart server để load database mới
docker-compose restart
```

### Kiểm tra version database

```bash
# Xem ngày sửa đổi file
ls -la dbs/GeoIP.dat dbs/GeoIPCity.dat
```

## 🛠️ Maintenance Tasks

### Dọn dẹp logs cũ

```bash
# Xóa logs cũ hơn 30 ngày
find logs/ -name "*.log" -mtime +30 -delete

# Hoặc nén logs cũ
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;
```

### Backup

```bash
# Backup tất cả dữ liệu
tar -czf backup_$(date +%Y%m%d).tar.gz dbs/ logs/

# Chỉ backup config
tar -czf backup_config_$(date +%Y%m%d).tar.gz \
    dbs/banned_ips.json \
    dbs/private_cidr.json \
    dbs/suspicious.txt \
    config.py
```

### Restore

```bash
# Restore từ backup
tar -xzf backup_20251205.tar.gz

# Restart server
docker-compose restart
```

## 🔐 Security Best Practices

### 1. Thay đổi tokens mặc định

```bash
# Tạo token mới
python -c "import secrets; print(secrets.token_hex(32))"

# Cập nhật trong environment
export ADMIN_TOKEN="new_secure_token_here"
export SECRET_KEY="new_secret_key_here"
```

### 2. Hạn chế quyền truy cập admin

**Nginx - Chỉ cho phép IP nội bộ:**
```nginx
location /admin {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    proxy_pass http://127.0.0.1:5000;
}
```

### 3. Rate limiting

**Nginx:**
```nginx
# Giới hạn 10 request/giây từ mỗi IP
limit_req_zone $binary_remote_addr zone=geoip:10m rate=10r/s;

location / {
    limit_req zone=geoip burst=20 nodelay;
    proxy_pass http://127.0.0.1:5000;
}
```

### 4. Giám sát bất thường

```bash
# Script kiểm tra số IP bị ban đột biến
# Lưu ý: Script này cần file banned_ips.json hợp lệ
BAN_COUNT=$(python -c "
import json
import sys
try:
    with open('dbs/banned_ips.json', 'r') as f:
        data = json.load(f)
        print(len(data.get('banned_ips', {})))
except (FileNotFoundError, json.JSONDecodeError):
    print(0)
")
if [ "$BAN_COUNT" -gt 100 ]; then
    echo "Warning: High number of banned IPs: $BAN_COUNT"
    # Gửi alert...
fi
```

## 📈 Performance Tuning

### Tăng workers

**Waitress:**
```python
serve(app, host='0.0.0.0', port=5000, threads=8)
```

**Gunicorn:**
```bash
gunicorn -w 4 --threads 2 -b 0.0.0.0:5000 geoip_proxy:app
```

### Docker resources

```yaml
deploy:
  resources:
    limits:
      cpus: "2"
      memory: "2G"
    reservations:
      cpus: "0.5"
      memory: "512M"
```

### Caching (nếu cần)

Có thể thêm Redis cache cho các lookup phổ biến:

```python
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_country_cached(ip):
    cached = cache.get(f"geoip:{ip}")
    if cached:
        return cached.decode()
    
    country = geoip.country_code_by_addr(ip)
    cache.setex(f"geoip:{ip}", 3600, country)  # Cache 1 giờ
    return country
```

## 🆘 Emergency Procedures

### Server không phản hồi

```bash
# Kiểm tra container
docker ps -a | grep geoip

# Restart
docker-compose restart

# Xem logs lỗi
docker logs --tail 50 geoip
```

### Bị tấn công DDoS

```bash
# 1. Xem top IPs
grep "$(date +%Y-%m-%d)" logs/*.log | cut -d' ' -f5 | sort | uniq -c | sort -rn | head -20

# 2. Ban các IP đáng ngờ
for ip in 1.2.3.4 5.6.7.8; do
    curl -X POST "http://localhost:5000/admin/ban/add?token=TOKEN&ip=$ip&reason=DDoS"
done

# 3. Hoặc block ở firewall
iptables -A INPUT -s 1.2.3.4 -j DROP
```

### Database bị corrupt

```bash
# Tải lại database
rm dbs/GeoIP.dat dbs/GeoIPCity.dat
wget -O dbs/GeoIP.dat.gz https://mailfud.org/geoip-legacy/GeoIP.dat.gz
wget -O dbs/GeoIPCity.dat.gz https://mailfud.org/geoip-legacy/GeoIPCity.dat.gz
gunzip -f dbs/*.gz

# Restart
docker-compose restart
```

---

➡️ **Tiếp theo**: [Xử lý sự cố](Troubleshooting) - Giải quyết các vấn đề thường gặp
