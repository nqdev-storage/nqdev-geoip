[![CodeQL](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/github-code-scanning/codeql)
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/nqdev-storage/nqdev-geoip/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/nqdev-storage/nqdev-geoip/tree/main)
[![Python App Flask CI](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/python-app-testing.yml/badge.svg)](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/python-app-testing.yml)
[![Update GeoIP Databases](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/geoip_update.yml/badge.svg)](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/geoip_update.yml)
[![Build and Push Docker Image](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/nqdev-storage/nqdev-geoip/actions/workflows/docker-publish.yml)

# 📌 nqdev-geoip

Nền tảng cung cấp miễn phí cơ sở dữ liệu GeoIP legacy và GeoLite2, cập nhật định kỳ, phục vụ nhu cầu tra cứu vị trí địa lý theo địa chỉ IP.

## 🔍 Giới thiệu

`nqdev-geoip` là dự án Python hỗ trợ:

-   Tra cứu vị trí IP bằng GeoIP legacy.
-   Sử dụng hoặc tích hợp các database chuẩn GeoLite2.
-   API Flask đơn giản để kiểm tra nhanh qua HTTP.
-   Tích hợp CI/CD, Docker, tự động cập nhật dữ liệu.

Phù hợp cho:

-   Các ứng dụng phân tích IP.
-   Hệ thống bảo mật.
-   Cần dữ liệu định vị nội bộ, không phụ thuộc dịch vụ bên thứ ba.

## ⚙️ Hướng dẫn cài đặt

### 1️⃣ Sử dụng môi trường ảo

```bash
pip install virtualenv
virtualenv venv -p E:\sys\services\Python\Python311\python.exe
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Backup/recover package:**

```bash
python -m pip freeze > requirements.txt
pip install -r requirements.txt
```

### 2️⃣ Khởi tạo database (nếu có)

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3️⃣ Chạy server Flask

```bash
python manage.py runserver 0.0.0.0:8000
```

## 📦 API RESTful

### 🛰 GeoIP Legacy - Country Lookup

```bash
curl --location 'http://localhost:5000/geoip?ip=185.213.82.249'
```

### 🌐 GeoIP Legacy - City Lookup

```bash
curl --location 'http://localhost:5000/geoipcity?ip=185.213.82.249'
```

### 📸 Instagram GetInfo (mẫu tham khảo)

```bash
curl --location 'http://localhost:5000/instagram/getinfo?username=bngoc.winwin'
```

## 📚 Sử dụng thư viện Python

```python
from nqdev_geoip import GeoIP

gi = GeoIP()
result = gi.lookup('8.8.8.8')

print(result)
# {
#   'country': 'US',
#   'country_name': 'United States',
#   ...
# }
```

## 🛠 Cập nhật dữ liệu

-   Tự động thông qua workflow CI/CD.
-   Có thể thủ công nếu cần:
    ```python
    from nqdev_geoip import GeoIP
    gi = GeoIP()
    gi.update_database()
    ```
-   Hoặc tải về trực tiếp tại:
    -   https://mailfud.org/geoip-legacy/
    -   Script: geoip_update.sh

## 📦 Docker Image

Docker hỗ trợ xây dựng và triển khai dễ dàng:

```bash
docker build -t nqdev-geoip .
docker run -p 5000:5000 nqdev-geoip
```

Docker Image chính thức sẽ được cập nhật qua workflow tự động.

## 🌐 GeoLite2.mmdb Database

Tích hợp GeoLite2 (Country, City, ASN) từ MaxMind:

### 📥 Tải nhanh:

-   [GeoLite2-ASN.mmdb](https://git.io/GeoLite2-ASN.mmdb)
-   [GeoLite2-City.mmdb](https://git.io/GeoLite2-City.mmdb)
-   [GeoLite2-Country.mmdb](https://git.io/GeoLite2-Country.mmdb)

### Hoặc từ mirror:

-   [GeoLite2-ASN.mmdb](https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-ASN.mmdb)
-   [GeoLite2-City.mmdb](https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb)
-   [GeoLite2-Country.mmdb](https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb)

## 📜 Lịch sử phiên bản (CHANGELOG)

Thông tin cập nhật và thay đổi của dự án được ghi chi tiết tại: ➡️ [Xem file CHANGELOG.md](/CHANGELOG.md)

## 🔐 Chính sách bảo mật

Vui lòng tham khảo chính sách công bố lỗ hổng bảo mật và quy trình báo cáo tại: ➡️ [Xem file SECURITY.md](/SECURITY.md)

## 📑 Giấy phép

-   GeoIP Legacy Database: Theo giấy phép nguồn mở từ [MaxMind](https://www.maxmind.com/).
-   GeoLite2 Database:
    -   © [MaxMind](https://www.maxmind.com/), Inc.
    -   [GeoLite2 End User License Agreement](https://www.maxmind.com/en/geolite2/eula)
    -   [Creative Commons License](https://creativecommons.org/licenses/by-sa/4.0/)

## ✅ Tổng kết

`nqdev-geoip` là một giải pháp miễn phí, hiệu quả, và dễ tích hợp cho các ứng dụng Python hoặc hệ thống backend có nhu cầu tra cứu vị trí địa lý IP, với khả năng cập nhật dữ liệu tự động qua CI/CD và Docker.

---

**👉 Đóng góp hoặc liên hệ:**
Hãy mở issue hoặc pull request nếu bạn có đề xuất nâng cấp hoặc phát hiện lỗi.
