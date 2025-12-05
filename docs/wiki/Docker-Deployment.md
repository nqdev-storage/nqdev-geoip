# 🐳 Docker Deployment

Hướng dẫn triển khai **nqdev-geoip** bằng Docker và Docker Compose.

## 📋 Yêu cầu

- Docker 20.x hoặc mới hơn
- Docker Compose 2.x hoặc mới hơn
- Ít nhất 256MB RAM
- Port 5000 hoặc 8002 (có thể thay đổi)

## 🚀 Quick Start

### Sử dụng Docker Image có sẵn

```bash
# Pull image mới nhất
docker pull ghcr.io/nqdev-storage/nqdev-geoip:latest

# Chạy container
docker run -d \
  --name geoip \
  -p 5000:5000 \
  ghcr.io/nqdev-storage/nqdev-geoip:latest
```

### Sử dụng Docker Compose

```bash
# Tải docker-compose.yml
curl -O https://raw.githubusercontent.com/nqdev-storage/nqdev-geoip/main/docker-compose.yml

# Khởi động
docker-compose up -d
```

## 📝 Docker Compose Configuration

### docker-compose.yml cơ bản

```yaml
services:
  geoip:
    image: ghcr.io/nqdev-storage/nqdev-geoip:latest
    container_name: geoip
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - ./dbs:/app/dbs
      - ./logs:/app/logs
    environment:
      - TZ=Asia/Ho_Chi_Minh
      - PYTHONUNBUFFERED=1
```

### docker-compose.yml đầy đủ (production)

```yaml
services:
  geoip:
    image: ghcr.io/nqdev-storage/nqdev-geoip:latest
    build:
      context: .
      dockerfile: ./Dockerfile
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
      - SECRET_KEY=your_secret_key_here
      - ADMIN_TOKEN=your_admin_token_here
    dns:
      - 8.8.8.8
      - 8.8.4.4
      - 1.1.1.1
      - 1.0.0.1
    deploy:
      resources:
        limits:
          cpus: "1"
          memory: "1G"
        reservations:
          cpus: "0.25"
          memory: "256M"
    logging:
      driver: "json-file"
      options:
        max-size: "100MB"
        max-file: "3"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

## 🔧 Build Docker Image

### Build từ Source

```bash
# Clone repository
git clone https://github.com/nqdev-storage/nqdev-geoip.git
cd nqdev-geoip

# Build image
docker build -t nqdev-geoip .

# Build với tag cụ thể
docker build -t nqdev-geoip:1.0.0 .

# Build không cache (fresh build)
docker build --no-cache -t nqdev-geoip .
```

### Dockerfile giải thích

```dockerfile
# Alpine Linux + Python 3.11 (nhẹ, an toàn)
FROM python:3.11.2-alpine3.16

# Metadata
LABEL maintainer="Nguyen Quy <quyit.job@gmail.com>"

# Working directory
WORKDIR /app

# Cài dependencies trước (tận dụng Docker cache)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . /app/

# Expose port (matching application default)
EXPOSE 5000

# Environment variables
ENV FLASK_APP=geoip_proxy.py
ENV FLASK_ENV=production

# Chạy bằng Waitress (production WSGI server)
CMD ["python", "waitress_geoip_proxy.py"]
```

## 📂 Volumes & Data Persistence

### Cấu trúc thư mục mount

```
project/
├── docker-compose.yml
├── dbs/
│   ├── GeoIP.dat           # GeoIP Country database
│   ├── GeoIPCity.dat       # GeoIP City database
│   ├── banned_ips.json     # IP ban list (auto-generated)
│   └── private_cidr.json   # Private CIDR config (optional)
└── logs/
    └── app_geoip_proxy_*.log  # Application logs
```

### Tạo thư mục cần thiết

```bash
mkdir -p dbs logs
chmod 755 dbs logs
```

### Download databases

```bash
# GeoIP Legacy
wget -O dbs/GeoIP.dat.gz https://mailfud.org/geoip-legacy/GeoIP.dat.gz
gunzip -f dbs/GeoIP.dat.gz

wget -O dbs/GeoIPCity.dat.gz https://mailfud.org/geoip-legacy/GeoIPCity.dat.gz
gunzip -f dbs/GeoIPCity.dat.gz
```

## 🌐 Reverse Proxy Configuration

### Nginx

```nginx
upstream geoip_backend {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name geoip.yourdomain.com;

    location / {
        proxy_pass http://geoip_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Nginx với SSL

```nginx
server {
    listen 443 ssl http2;
    server_name geoip.yourdomain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}

server {
    listen 80;
    server_name geoip.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Traefik (docker-compose)

```yaml
services:
  geoip:
    image: ghcr.io/nqdev-storage/nqdev-geoip:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.geoip.rule=Host(`geoip.yourdomain.com`)"
      - "traefik.http.routers.geoip.entrypoints=websecure"
      - "traefik.http.routers.geoip.tls.certresolver=letsencrypt"
      - "traefik.http.services.geoip.loadbalancer.server.port=5000"
```

## 📊 Monitoring & Logging

### Xem logs container

```bash
# Logs real-time
docker logs -f geoip

# Logs với timestamp
docker logs --timestamps geoip

# 100 dòng logs cuối
docker logs --tail 100 geoip

# Logs từ thời điểm cụ thể
docker logs --since 2024-01-01T00:00:00 geoip
```

### Docker Compose logs

```bash
# Tất cả services
docker-compose logs -f

# Chỉ geoip service
docker-compose logs -f geoip
```

### Health check

```bash
# Kiểm tra trạng thái container
docker ps

# Chi tiết container
docker inspect geoip

# Health status
docker inspect --format='{{.State.Health.Status}}' geoip
```

## 🔄 Updates & Maintenance

### Cập nhật image

```bash
# Pull image mới
docker pull ghcr.io/nqdev-storage/nqdev-geoip:latest

# Restart container
docker-compose down
docker-compose up -d
```

### Backup data

```bash
# Backup databases
tar -czf backup_dbs_$(date +%Y%m%d).tar.gz dbs/

# Backup logs
tar -czf backup_logs_$(date +%Y%m%d).tar.gz logs/
```

### Xóa dữ liệu cũ

```bash
# Xóa container và images không dùng
docker system prune -f

# Xóa cả volumes không dùng
docker system prune -a --volumes
```

## 🛠 Troubleshooting

### Container không start

```bash
# Xem logs chi tiết
docker logs geoip

# Kiểm tra cấu hình
docker-compose config

# Chạy interactive để debug
docker run -it --rm nqdev-geoip /bin/sh
```

### Port conflict

```bash
# Tìm process đang dùng port
lsof -i :5000

# Hoặc đổi port trong docker-compose.yml
ports:
  - "8080:5000"  # Map port 8080 thay vì 5000
```

### Database không load

```bash
# Kiểm tra file tồn tại
ls -la dbs/

# Kiểm tra quyền
chmod 644 dbs/GeoIP.dat dbs/GeoIPCity.dat

# Mount volume đúng cách
docker run -v $(pwd)/dbs:/app/dbs nqdev-geoip
```

### Memory issues

```yaml
# Tăng giới hạn memory trong docker-compose.yml
deploy:
  resources:
    limits:
      memory: "2G"
    reservations:
      memory: "512M"
```

## 📋 Docker Commands Quick Reference

| Command | Mô tả |
|---------|-------|
| `docker-compose up -d` | Khởi động services |
| `docker-compose down` | Dừng và xóa containers |
| `docker-compose restart` | Restart services |
| `docker-compose logs -f` | Xem logs real-time |
| `docker-compose ps` | Liệt kê containers |
| `docker-compose pull` | Pull images mới |
| `docker-compose build` | Build lại images |
| `docker exec -it geoip /bin/sh` | Shell vào container |

---

➡️ **Tiếp theo**: [Cấu hình](Configuration) - Các tùy chọn cấu hình
