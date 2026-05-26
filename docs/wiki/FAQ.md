# ❓ Câu hỏi thường gặp (FAQ)

Các câu hỏi thường gặp về **nqdev-geoip**.

## 🌐 Chung

### Q: nqdev-geoip là gì?

**A**: nqdev-geoip là một REST API service miễn phí cung cấp tra cứu vị trí địa lý từ địa chỉ IP. Service sử dụng GeoIP Legacy và GeoLite2 databases, được cập nhật tự động hàng tuần qua CI/CD.

### Q: nqdev-geoip có miễn phí không?

**A**: Có, hoàn toàn miễn phí và open source. Bạn có thể tự host hoặc sử dụng source code cho mục đích cá nhân và thương mại.

### Q: Độ chính xác của dữ liệu như thế nào?

**A**: 
- **Country level**: ~99% chính xác
- **City level**: ~80-90% chính xác (phụ thuộc vào ISP và region)
- **Coordinates**: Có thể sai lệch vài km đến vài chục km

Lưu ý: GeoIP databases không thể chính xác 100% do tính chất động của IP allocation.

### Q: Có giới hạn số lượng request không?

**A**: Không có giới hạn mặc định từ application. Tuy nhiên, bạn nên cấu hình rate limiting tại reverse proxy (Nginx) để tránh abuse.

### Q: Database được cập nhật bao lâu một lần?

**A**: Tự động cập nhật mỗi tuần (Chủ Nhật 00:00 UTC) qua GitHub Actions workflow.

## 🔧 Cài đặt & Triển khai

### Q: Yêu cầu hệ thống tối thiểu là gì?

**A**:
- **CPU**: 0.5 core
- **RAM**: 256MB (khuyến nghị 512MB)
- **Disk**: 100MB (cho databases và logs)
- **Python**: 3.11+ (hoặc Docker)

### Q: Có thể chạy trên Windows không?

**A**: Có, hỗ trợ đầy đủ Windows 10/11. Sử dụng:
- Python virtual environment
- Docker Desktop for Windows
- WSL2 (khuyến nghị)

### Q: Làm sao để chạy trên port khác 5000?

**A**:
```bash
# Python
python geoip_proxy.py --port 8000

# Docker
docker run -p 8000:5000 nqdev-geoip

# Docker Compose
# Sửa docker-compose.yml:
ports:
  - "8000:5000"
```

### Q: Có thể chạy nhiều instances không?

**A**: Có, application là stateless. Chạy nhiều containers và dùng load balancer:

```yaml
# docker-compose.yml
services:
  geoip1:
    image: ghcr.io/nqdev-storage/nqdev-geoip:latest
    ports:
      - "5001:5000"
  
  geoip2:
    image: ghcr.io/nqdev-storage/nqdev-geoip:latest
    ports:
      - "5002:5000"
```

## 🔐 Bảo mật

### Q: Làm sao để bảo vệ admin endpoints?

**A**:
1. **Thay đổi ADMIN_TOKEN** mặc định
2. **Sử dụng HTTPS** trong production
3. **IP whitelist** tại Nginx:
   ```nginx
   location /admin {
       allow 192.168.1.0/24;
       deny all;
   }
   ```
4. **Rate limiting** tại reverse proxy

### Q: IP của tôi bị ban nhầm, làm sao để unban?

**A**:
```bash
# Method 1: Sử dụng admin API
curl -X POST "http://localhost:5000/admin/ban/unban?token=YOUR_TOKEN&ip=YOUR_IP"

# Method 2: Sửa trực tiếp file
nano dbs/banned_ips.json
# Xóa IP của bạn, save và restart server

# Method 3: Xóa tất cả bans
echo '{"banned_ips": {}}' > dbs/banned_ips.json
docker-compose restart
```

### Q: Làm sao để thêm suspicious patterns tùy chỉnh?

**A**:
```bash
# Thêm vào dbs/suspicious.txt
echo "/my-custom-pattern" >> dbs/suspicious.txt

# Restart server
docker-compose restart
```

### Q: Tại sao admin endpoints không bị ban check?

**A**: Để tránh khóa admin. Nếu admin IP bị ban nhầm, họ vẫn có thể truy cập admin API để tự unban. Đây là safety mechanism.

## 📡 API Usage

### Q: Làm sao để tra cứu IP của client đang request?

**A**: Sử dụng IP từ request header:

```python
import requests

# Get client's public IP
response = requests.get('https://api.ipify.org?format=json')
client_ip = response.json()['ip']

# Lookup
geoip_response = requests.get(f'http://localhost:5000/geoip?ip={client_ip}')
print(geoip_response.json())
```

### Q: API có hỗ trợ IPv6 không?

**A**: Có, GeoIP databases hỗ trợ cả IPv4 và IPv6. Tuy nhiên, độ chính xác của IPv6 có thể thấp hơn IPv4.

### Q: Làm sao để tra cứu nhiều IPs cùng lúc?

**A**: API không hỗ trợ batch lookup. Bạn cần gọi API nhiều lần:

```python
import requests
from concurrent.futures import ThreadPoolExecutor

ips = ['8.8.8.8', '1.1.1.1', '208.67.222.222']

def lookup_ip(ip):
    response = requests.get(f'http://localhost:5000/geoip?ip={ip}')
    return response.json()

with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(lookup_ip, ips))

print(results)
```

### Q: Tại sao private IPs (192.168.x.x) trả về lỗi?

**A**: Private IPs không có trong GeoIP database. Bạn có thể cấu hình default response:

```json
// dbs/private_cidr_config.json
{
  "private_cidrs": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
  "default_response": {
    "country_code": "VN",
    "country_name": "Vietnam",
    "city": "Private Network"
  }
}
```

### Q: Response time bao lâu?

**A**: 
- **Average**: 10-50ms
- **P95**: <100ms
- **P99**: <200ms

Phụ thuộc vào server resources và network latency.

## 🐳 Docker

### Q: Làm sao để update Docker image?

**A**:
```bash
# Pull latest image
docker pull ghcr.io/nqdev-storage/nqdev-geoip:latest

# Restart containers
docker-compose down
docker-compose up -d
```

### Q: Làm sao để xem logs trong Docker?

**A**:
```bash
# Real-time logs
docker logs -f geoip

# Last 100 lines
docker logs --tail 100 geoip

# Logs with timestamps
docker logs --timestamps geoip
```

### Q: Container không start, làm sao debug?

**A**:
```bash
# Xem logs
docker logs geoip

# Chạy interactive shell
docker run -it --rm ghcr.io/nqdev-storage/nqdev-geoip:latest /bin/sh

# Kiểm tra config
docker-compose config

# Rebuild image
docker-compose build --no-cache
```

### Q: Làm sao để mount custom databases?

**A**:
```yaml
# docker-compose.yml
volumes:
  - ./my-custom-dbs:/app/dbs
```

## 🔄 Database Updates

### Q: Làm sao để update databases thủ công?

**A**:
```bash
# Download databases
wget -O dbs/GeoIP.dat.gz https://mailfud.org/geoip-legacy/GeoIP.dat.gz
gunzip -f dbs/GeoIP.dat.gz

wget -O dbs/GeoIPCity.dat.gz https://mailfud.org/geoip-legacy/GeoIPCity.dat.gz
gunzip -f dbs/GeoIPCity.dat.gz

# Restart server
docker-compose restart
```

### Q: Có thể sử dụng GeoLite2 .mmdb thay vì .dat không?

**A**: Hiện tại application chỉ hỗ trợ GeoIP Legacy (.dat format). Để sử dụng GeoLite2 .mmdb, bạn cần:
1. Cài đặt `maxminddb` library
2. Sửa code để sử dụng `maxminddb.Reader` thay vì `pygeoip.GeoIP`

### Q: Database bị corrupt, làm sao fix?

**A**:
```bash
# Xóa databases cũ
rm dbs/GeoIP.dat dbs/GeoIPCity.dat

# Download lại
wget -O dbs/GeoIP.dat.gz https://mailfud.org/geoip-legacy/GeoIP.dat.gz
wget -O dbs/GeoIPCity.dat.gz https://mailfud.org/geoip-legacy/GeoIPCity.dat.gz
gunzip -f dbs/*.gz

# Restart
docker-compose restart
```

## 🛠️ Troubleshooting

### Q: API trả về 403 Forbidden?

**A**: IP của bạn đã bị ban. Xem [Security FAQ](#q-ip-của-tôi-bị-ban-nhầm-làm-sao-để-unban) để unban.

### Q: API trả về 404 Not Found?

**A**: 
- IP không có trong database (có thể là IP mới hoặc private IP)
- Database chưa được download
- Database bị corrupt

### Q: Server không start?

**A**: Kiểm tra:
1. Port 5000 có bị chiếm không: `lsof -i :5000`
2. Databases có tồn tại không: `ls -la dbs/`
3. Dependencies đã cài đủ chưa: `pip list`
4. Logs: `tail -100 logs/*.log`

### Q: Performance chậm?

**A**:
1. Tăng workers: `serve(app, threads=8)`
2. Sử dụng reverse proxy caching
3. Tăng resources cho Docker container
4. Kiểm tra database size: `ls -lh dbs/*.dat`

## 🔗 Tích hợp

### Q: Làm sao để tích hợp với Nginx?

**A**: Xem [Docker Deployment - Reverse Proxy Configuration](Docker-Deployment#-reverse-proxy-configuration)

### Q: Có thể sử dụng với Cloudflare không?

**A**: Có, nhưng lưu ý:
- Cloudflare thêm header `CF-Connecting-IP`
- Application sử dụng `X-Forwarded-For` (ProxyFix middleware)
- Cấu hình Nginx để forward đúng header

### Q: Làm sao để monitor với Prometheus?

**A**: Tạo custom exporter:

```python
from prometheus_client import Counter, Histogram, start_http_server

request_count = Counter('geoip_requests_total', 'Total requests')
request_duration = Histogram('geoip_request_duration_seconds', 'Request duration')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_count.inc()
    duration = time.time() - request.start_time
    request_duration.observe(duration)
    return response

# Start metrics server
start_http_server(9090)
```

## 📊 Performance

### Q: Có thể handle bao nhiêu requests/second?

**A**: Phụ thuộc vào hardware:
- **1 CPU, 512MB RAM**: ~100-200 req/s
- **2 CPU, 1GB RAM**: ~500-1000 req/s
- **4 CPU, 2GB RAM**: ~2000-5000 req/s

Với reverse proxy caching, có thể đạt 10,000+ req/s.

### Q: Làm sao để tối ưu performance?

**A**:
1. **Tăng workers**: Waitress threads hoặc Gunicorn workers
2. **Caching**: Nginx proxy_cache
3. **CDN**: Cloudflare hoặc AWS CloudFront
4. **Load balancing**: Multiple instances
5. **Database optimization**: Đảm bảo databases được load vào memory

## 💡 Best Practices

### Q: Nên sử dụng GeoIP hay GeoIPCity?

**A**:
- **GeoIP** (`/geoip`): Nhanh hơn, chỉ trả về country code
- **GeoIPCity** (`/geoipcity`): Chậm hơn, trả về đầy đủ thông tin

Sử dụng `/geoip` nếu chỉ cần country, `/geoipcity` nếu cần city/coordinates.

### Q: Có nên cache responses không?

**A**: Có, nên cache:
- **TTL**: 1-24 giờ (IP allocation ít thay đổi)
- **Cache key**: IP address
- **Implementation**: Redis hoặc Nginx proxy_cache

### Q: Làm sao để backup dữ liệu?

**A**:
```bash
# Backup databases và configs
tar -czf backup_$(date +%Y%m%d).tar.gz dbs/ logs/

# Restore
tar -xzf backup_20260526.tar.gz
docker-compose restart
```

## 📞 Hỗ trợ

### Q: Tôi gặp vấn đề không có trong FAQ?

**A**:
1. Kiểm tra [Troubleshooting](Troubleshooting)
2. Tìm trong [GitHub Issues](https://github.com/nqdev-storage/nqdev-geoip/issues)
3. Tạo issue mới với:
   - Mô tả chi tiết vấn đề
   - Logs liên quan
   - Môi trường (OS, Docker version, etc.)
4. Liên hệ: quyit.job@gmail.com

### Q: Làm sao để đóng góp cho project?

**A**: Xem [Development Guide](Development) để biết chi tiết về:
- Setup development environment
- Code style guidelines
- Testing requirements
- Pull request process

---

⬅️ **Quay lại**: [Home](Home) - Trang chủ Wiki
