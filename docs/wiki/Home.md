# 📌 nqdev-geoip Wiki

Chào mừng bạn đến với Wiki hướng dẫn sử dụng **nqdev-geoip** - Nền tảng tra cứu vị trí địa lý theo địa chỉ IP miễn phí.

## 🎯 Giới thiệu

**nqdev-geoip** là một dự án Python/Flask cung cấp API RESTful để tra cứu thông tin địa lý từ địa chỉ IP. Dự án hỗ trợ:

- ✅ Tra cứu quốc gia từ IP (GeoIP Legacy)
- ✅ Tra cứu thành phố từ IP (GeoIP City)
- ✅ Tích hợp GeoLite2 database từ MaxMind
- ✅ API Swagger/OpenAPI documentation
- ✅ Hỗ trợ Docker deployment
- ✅ Tự động cập nhật database qua CI/CD
- ✅ Bảo mật với tính năng IP banning

## 📚 Mục lục

### Bắt đầu
| Trang | Mô tả |
|-------|-------|
| [Installation](Installation) | Hướng dẫn cài đặt và thiết lập môi trường |
| [Docker Deployment](Docker-Deployment) | Triển khai bằng Docker và Docker Compose |

### Tài liệu kỹ thuật
| Trang | Mô tả |
|-------|-------|
| [API Reference](API-Reference) | Tài liệu tham khảo đầy đủ về các API endpoints |
| [Architecture](Architecture) | Kiến trúc hệ thống và thiết kế |
| [Security](Security) | Tính năng bảo mật và best practices |

### Vận hành
| Trang | Mô tả |
|-------|-------|
| [Configuration](Configuration) | Các tùy chọn cấu hình hệ thống |
| [Admin Guide](Admin-Guide) | Hướng dẫn quản trị và quản lý IP ban |
| [Troubleshooting](Troubleshooting) | Giải quyết các vấn đề thường gặp |

### Phát triển
| Trang | Mô tả |
|-------|-------|
| [Development](Development) | Hướng dẫn phát triển và đóng góp |
| [CI/CD](CI-CD) | Pipeline tự động và deployment |

## 🚀 Bắt đầu nhanh

### 1. Cài đặt cơ bản

```bash
# Clone repository
git clone https://github.com/nqdev-storage/nqdev-geoip.git
cd nqdev-geoip

# Tạo môi trường ảo
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: .\venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
python geoip_proxy.py
```

### 2. Sử dụng Docker (khuyến nghị)

```bash
# Sử dụng Docker Compose
docker-compose up -d

# Hoặc build và chạy thủ công
docker build -t nqdev-geoip .
docker run -p 5000:5000 nqdev-geoip
```

### 3. Thử nghiệm API

```bash
# Tra cứu quốc gia
curl "http://localhost:5000/geoip?ip=8.8.8.8"

# Tra cứu thành phố
curl "http://localhost:5000/geoipcity?ip=8.8.8.8"
```

## 📊 Kiến trúc hệ thống

```
nqdev-geoip/
├── geoip_proxy.py          # Flask application chính
├── config.py               # Cấu hình ứng dụng
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker build configuration
├── docker-compose.yml      # Docker Compose configuration
├── dbs/                    # GeoIP databases
│   ├── GeoIP.dat          # GeoIP Legacy Country database
│   └── GeoIPCity.dat      # GeoIP Legacy City database
├── routes/                 # Flask route blueprints
│   ├── ip2location_routes.py
│   ├── user_routes.py
│   └── admin/
│       └── ban_routes.py  # Admin IP ban routes
├── utils/                  # Utility modules
│   ├── ip_ban.py          # IP banning functionality
│   ├── private_cidr.py    # Private CIDR handling
│   └── response_helper.py # Response formatting
└── tests/                  # Unit tests
```

## 🔗 Links hữu ích

- **Repository**: [github.com/nqdev-storage/nqdev-geoip](https://github.com/nqdev-storage/nqdev-geoip)
- **API Documentation**: `http://localhost:5000/apidocs/` (khi server đang chạy)
- **Docker Image**: `ghcr.io/nqdev-storage/nqdev-geoip:latest`
- **GeoLite2 Database**: [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)

## 📄 Giấy phép

- **GeoIP Legacy Database**: Theo giấy phép nguồn mở từ [MaxMind](https://www.maxmind.com/)
- **GeoLite2 Database**: © [MaxMind](https://www.maxmind.com/), Inc. - [GeoLite2 EULA](https://www.maxmind.com/en/geolite2/eula)

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:
1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📞 Liên hệ

- **Maintainer**: Nguyen Quy
- **Email**: quyit.job@gmail.com
- **Issues**: [GitHub Issues](https://github.com/nqdev-storage/nqdev-geoip/issues)
