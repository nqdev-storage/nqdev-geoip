# 📡 API Reference

Tài liệu tham khảo đầy đủ về các API endpoints của **nqdev-geoip**.

## 🌐 Base URL

- **Development**: `http://localhost:5000`
- **Production**: `https://your-domain.com`

## 📖 Swagger Documentation

API documentation tương tác có sẵn tại: `/apidocs/`

## 🔑 Authentication

Một số API yêu cầu `token` để xác thực. Token được truyền qua query parameter.

```bash
curl "http://localhost:5000/api/endpoint?token=your_admin_token"
```

---

## 📍 GeoIP Endpoints

### GET /

**Mô tả**: Trang chủ API - Kiểm tra server hoạt động

**Request:**
```bash
curl http://localhost:5000/
```

**Response:**
```
Welcome to Flask!
```

---

### GET /geoip

**Mô tả**: Tra cứu mã quốc gia từ địa chỉ IP (GeoIP Legacy)

**Parameters:**

| Tên | Loại | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| `ip` | string | ✅ | Địa chỉ IP cần tra cứu |
| `token` | string | ❌ | Token xác thực (tùy chọn) |

**Request:**
```bash
curl "http://localhost:5000/geoip?ip=8.8.8.8"
```

**Response thành công (200):**
```json
{
  "country": "US"
}
```

**Response lỗi - Thiếu IP (400):**
```json
{
  "error": "Missing IP address"
}
```

**Response lỗi - Không tìm thấy (404):**
```json
{
  "error": "IP address not found"
}
```

**Response lỗi - Server error (500):**
```json
{
  "error": "Internal server error"
}
```

**Ví dụ với các IP khác:**
```bash
# Google DNS (US)
curl "http://localhost:5000/geoip?ip=8.8.8.8"
# {"country":"US"}

# Cloudflare DNS (varies)
curl "http://localhost:5000/geoip?ip=1.1.1.1"
# {"country":"AU"}

# Vietnam IP
curl "http://localhost:5000/geoip?ip=113.160.92.3"
# {"country":"VN"}
```

---

### GET /geoipcity

**Mô tả**: Tra cứu thông tin chi tiết thành phố từ địa chỉ IP (GeoIP City)

**Parameters:**

| Tên | Loại | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| `ip` | string | ✅ | Địa chỉ IP cần tra cứu |
| `token` | string | ❌ | Token xác thực (tùy chọn) |

**Request:**
```bash
curl "http://localhost:5000/geoipcity?ip=185.213.82.249"
```

**Response thành công (200):**
```json
{
  "city": "Frankfurt am Main",
  "region_code": "HE",
  "area_code": 0,
  "time_zone": "Europe/Berlin",
  "dma_code": 0,
  "metro_code": null,
  "country_code3": "DEU",
  "latitude": 50.1109,
  "postal_code": "60311",
  "longitude": 8.6821,
  "country_code": "DE",
  "country_name": "Germany",
  "continent": "EU"
}
```

**Response lỗi - Thiếu IP (400):**
```json
{
  "error": "Missing IP address"
}
```

**Response lỗi - Invalid value (400):**
```json
{
  "error": "Invalid value provided"
}
```

**Response lỗi - Không tìm thấy (404):**
```json
{
  "error": "IP address not found"
}
```

---

### GET /geoip-update

**Mô tả**: Cập nhật database GeoIP (yêu cầu token)

**Parameters:**

| Tên | Loại | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| `token` | string | ✅ | Token xác thực admin |

**Request:**
```bash
curl "http://localhost:5000/geoip-update?token=your_admin_token"
```

**Response thành công (200):**
```json
{
  "isSuccess": true,
  "message": "Successfully updated the GeoIP database.",
  "payload": {}
}
```

**Response lỗi - Thiếu token (101):**
```json
{
  "isSuccess": false,
  "message": "Missing Token"
}
```

---

## 👤 User Endpoints

### GET /user/profile/{username}

**Mô tả**: Lấy thông tin profile người dùng

**Parameters:**

| Tên | Loại | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| `username` | string (path) | ✅ | Tên người dùng |

**Request:**
```bash
curl "http://localhost:5000/user/profile/johndoe"
```

**Response thành công (200):**
```json
{
  "isSuccess": true,
  "message": "Successfully",
  "payload": {
    "username": "johndoe"
  }
}
```

---

## 🌍 IP2Location Endpoints

### GET /ip2location/download/{db_code}

**Mô tả**: Tải database IP2Location theo mã code

**Parameters:**

| Tên | Loại | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| `db_code` | string (path) | ✅ | Mã database IP2Location (ví dụ: DB3.LITE, DB5.LITE) |

**Request:**
```bash
curl "http://localhost:5000/ip2location/download/DB3.LITE"
```

**Response thành công (200):**
```json
{
  "isSuccess": true,
  "message": "Lấy thông tin user thành công",
  "payload": {
    "db_code": "DB3.LITE"
  }
}
```

**Database codes hỗ trợ:**
- `DB3.LITE` - IPV6-COUNTRY-REGION-CITY
- `DB5.LITE` - IPV6-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE
- `DB9.LITE` - IPV6-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE
- `DB11.LITE` - IPV6-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE

---

## 🛡️ Admin Endpoints

### GET /admin/ban/list

**Mô tả**: Lấy danh sách IP đang bị cấm

**Parameters:**

| Tên | Loại | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| `token` | string | ✅ | Token xác thực admin |

**Request:**
```bash
curl "http://localhost:5000/admin/ban/list?token=your_admin_token"
```

**Response thành công (200):**
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

**Response lỗi - Token không hợp lệ (401):**
```json
{
  "isSuccess": false,
  "message": "Invalid or missing token"
}
```

---

### POST /admin/ban/add

**Mô tả**: Thêm IP vào danh sách cấm

**Parameters:**

| Tên | Loại | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| `token` | string | ✅ | Token xác thực admin |
| `ip` | string | ✅ | Địa chỉ IP cần cấm |
| `reason` | string | ❌ | Lý do cấm (mặc định: "Manual ban by admin") |

**Request:**
```bash
curl -X POST "http://localhost:5000/admin/ban/add?token=your_admin_token&ip=192.168.1.100&reason=Spam%20requests"
```

**Response thành công (200):**
```json
{
  "isSuccess": true,
  "message": "IP 192.168.1.100 has been banned"
}
```

**Response lỗi - Thiếu IP (400):**
```json
{
  "isSuccess": false,
  "message": "Missing IP address"
}
```

---

### POST /admin/ban/unban

**Mô tả**: Xóa IP khỏi danh sách cấm

**Parameters:**

| Tên | Loại | Bắt buộc | Mô tả |
|-----|------|----------|-------|
| `token` | string | ✅ | Token xác thực admin |
| `ip` | string | ✅ | Địa chỉ IP cần bỏ cấm |

**Request:**
```bash
curl -X POST "http://localhost:5000/admin/ban/unban?token=your_admin_token&ip=192.168.1.100"
```

**Response thành công (200):**
```json
{
  "isSuccess": true,
  "message": "IP 192.168.1.100 has been unbanned"
}
```

**Response lỗi - IP không tìm thấy (404):**
```json
{
  "isSuccess": false,
  "message": "IP not found in ban list"
}
```

---

## 📊 Response Format

### Standard Success Response

```json
{
  "isSuccess": true,
  "message": "Description of success",
  "payload": {
    // Data object
  }
}
```

### Standard Error Response

```json
{
  "isSuccess": false,
  "message": "Description of error"
}
```

### Simple Response (GeoIP endpoints)

```json
{
  "country": "US"
}
```

hoặc

```json
{
  "error": "Error description"
}
```

---

## 🔒 Rate Limiting & Security

### Automatic IP Banning

Server tự động ban các IP có request đáng ngờ như:
- Truy cập `/wp-admin`, `/wp-login`
- Truy cập `/phpMyAdmin`, `/phpmyadmin`
- Path traversal attacks (`../`, `%2e%2e/`)
- Các file PHP scan (`*.php`)

### Blocked Request Response

Khi IP bị ban, tất cả request sẽ nhận:

```json
{
  "error": "Access denied"
}
```
HTTP Status: `403 Forbidden`

---

## 🧪 Testing Examples

### Sử dụng cURL

```bash
# Basic country lookup
curl "http://localhost:5000/geoip?ip=8.8.8.8"

# City lookup with verbose
curl -v "http://localhost:5000/geoipcity?ip=185.213.82.249"

# Admin: List banned IPs
curl "http://localhost:5000/admin/ban/list?token=your_token"

# Admin: Ban an IP
curl -X POST "http://localhost:5000/admin/ban/add?token=your_token&ip=1.2.3.4&reason=Test"
```

### Sử dụng Python requests

```python
import requests

# Country lookup
response = requests.get('http://localhost:5000/geoip', params={'ip': '8.8.8.8'})
print(response.json())  # {'country': 'US'}

# City lookup
response = requests.get('http://localhost:5000/geoipcity', params={'ip': '185.213.82.249'})
print(response.json())

# Admin: Get ban list
response = requests.get('http://localhost:5000/admin/ban/list', 
                        params={'token': 'your_admin_token'})
print(response.json())
```

### Sử dụng JavaScript fetch

```javascript
// Country lookup
fetch('http://localhost:5000/geoip?ip=8.8.8.8')
  .then(res => res.json())
  .then(data => console.log(data));  // {country: "US"}

// City lookup
fetch('http://localhost:5000/geoipcity?ip=185.213.82.249')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 📋 HTTP Status Codes

| Code | Mô tả |
|------|-------|
| 200 | Thành công |
| 400 | Bad Request - Thiếu tham số hoặc giá trị không hợp lệ |
| 401 | Unauthorized - Token không hợp lệ hoặc thiếu |
| 403 | Forbidden - IP bị ban |
| 404 | Not Found - IP không tìm thấy trong database |
| 500 | Internal Server Error |

---

➡️ **Tiếp theo**: [Docker Deployment](Docker-Deployment) - Triển khai bằng Docker
