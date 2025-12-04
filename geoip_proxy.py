from flask import Flask, request, jsonify
from flasgger import Swagger
from werkzeug.middleware.proxy_fix import ProxyFix
import pygeoip
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

from routes.ip2location_routes import ip2location_bp
from routes.user_routes import user_bp

from geoip_update import download_and_extract, url_geoip, url_geoip_city
from utils.response_helper import okResult
from utils.ip_ban import (
    is_ip_banned, ban_ip, unban_ip, get_ban_list,
    is_suspicious_request, get_client_ip
)

# Phiên bản ứng dụng
__version__ = "1.0.0"

# Cấu hình logger
logging.basicConfig(
    # Chọn mức độ log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',  # Định dạng log
    handlers=[
        logging.StreamHandler(),  # Ghi log ra console
        # Ghi log vào file, tách theo ngày
        TimedRotatingFileHandler(
            filename=f"logs/app_geoip_proxy_{datetime.datetime.now().strftime('%Y%m%d')}.log",
            when="midnight",    # Tách log vào lúc nửa đêm
            interval=1,         # Sau mỗi ngày
            backupCount=7,      # Lưu tối đa 7 ngày log cũ
            encoding='utf-8',    # Đặt mã hóa file log để hỗ trợ ký tự Unicode.
        )
    ]
)

# https://flask.palletsprojects.com/en/stable/
app = Flask(__name__)
app.config.from_object('config.Config')  # Load your config
# Initialize Swagger
Swagger(app=app)

# Xử lý reverse proxy (nếu có) - ví dụ khi ứng dụng chạy sau Nginx hoặc HAProxy
app.wsgi_app = ProxyFix(app.wsgi_app)

# Register blueprints
app.register_blueprint(ip2location_bp)
app.register_blueprint(user_bp)

# Tải tệp GeoIP for V2Ray
# Thay đổi đường dẫn tới tệp `.dat` của bạn
GeoIP_path = './dbs/GeoIP.dat'
geoip = pygeoip.GeoIP(GeoIP_path)

# Tải tệp GeoIPCity cho V2Ray
GeoIPCity_path = './dbs/GeoIPCity.dat'
GeoIPCity = pygeoip.GeoIP(GeoIPCity_path)

# Admin endpoints exempt from IP ban checks
ADMIN_ENDPOINTS = ['/admin/ban-list', '/admin/ban', '/admin/unban']


def validate_admin_token(token: str) -> bool:
    """Validate admin token against configured value."""
    expected_token = app.config.get('ADMIN_TOKEN', 'your_admin_token_here')
    return token == expected_token


@app.before_request
def check_banned_ip():
    """
    Middleware kiểm tra IP bị cấm và phát hiện request đáng ngờ.
    Tự động ban IP nếu phát hiện request đáng ngờ.
    Admin endpoints được miễn kiểm tra để tránh khóa admin.
    """
    # Exempt admin endpoints from ban checks
    if request.path in ADMIN_ENDPOINTS:
        return None

    client_ip = get_client_ip(request)

    # Kiểm tra nếu IP đã bị ban
    if is_ip_banned(client_ip):
        logging.warning(f"Blocked request from banned IP: {client_ip} - {request.path}")
        return jsonify({"error": "Access denied"}), 403

    # Phát hiện request đáng ngờ và tự động ban IP
    if is_suspicious_request(request.path):
        logging.warning(f"Suspicious request detected from IP: {client_ip} - {request.path}")
        ban_ip(client_ip, reason=f"Suspicious request: {request.path}")
        return jsonify({"error": "Access denied"}), 403


@app.route(rule='/', methods=['GET'])
def home():
    """
    Trang chủ API
    ---
    responses:
      200:
        description: Welcome message
    """
    return "Welcome to Flask!"


@app.route(rule='/geoip-update', methods=['GET'])
def get_geoip_update():
    """
    Cập nhật thông tin GeoIP từ nguồn dữ liệu mailfud.org
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: Token xác thực
    responses:
      101:
        description: Missing Token
      200:
        description: Successfully updated the GeoIP database.
      404:
        description: Không tìm thấy địa chỉ IP
      500:
        description: Exception occurred
    """
    token = request.args.get('token')
    if not token:
        return okResult(isSuccess=False, message="Missing Token", http_code=101)

        # Lấy thông tin địa lý từ địa chỉ IP
    try:
        # download_and_extract(url_geoip, './dbs/GeoIP.dat')
        # download_and_extract(url_geoip_city, './dbs/GeoIPCity.dat')

        return okResult(isSuccess=True, message="Successfully updated the GeoIP database.", payload={}, http_code=200)
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        return okResult(isSuccess=False, message="Exception occurred", http_code=500)


@app.route(rule='/geoip', methods=['GET'])
def get_geoip_info():
    """
    Lấy thông tin quốc gia từ địa chỉ IP
    ---
    parameters:
      - name: ip
        in: query
        type: string
        required: true
        description: Địa chỉ IP cần tra cứu
    responses:
      200:
        description: Trả về mã quốc gia
        schema:
          type: object
          properties:
            country:
              type: string
      400:
        description: Thiếu IP
      404:
        description: Không tìm thấy IP
    """
    ip = request.args.get('ip')
    token = request.args.get('token')
    if not ip:
        return jsonify({"error": "Missing IP address"}), 400

    # Lấy thông tin quốc gia từ địa chỉ IP
    try:
        country = geoip.country_code_by_addr(ip)
        if country:
            return jsonify({"country": country})
        else:
            return jsonify({"error": "IP address not found"}), 404
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route(rule='/geoipcity', methods=['GET'])
def get_geoip_city_info():
    """
    Lấy thông tin thành phố từ địa chỉ IP
    ---
    parameters:
      - name: ip
        in: query
        type: string
        required: true
        description: Địa chỉ IP cần tra cứu
      - name: token
        in: query
        type: string
        required: false
        description: Token xác thực
    responses:
      200:
        description: Trả về thông tin thành phố
        schema:
          type: object
      400:
        description: Thiếu IP hoặc giá trị không hợp lệ
      404:
        description: Không tìm thấy địa chỉ IP
      500:
        description: Lỗi server
    """
    ip = request.args.get('ip')
    token = request.args.get('token')
    if not ip:
        return jsonify({"error": "Missing IP address"}), 400

    # Lấy thông tin địa lý từ địa chỉ IP
    try:
        city = GeoIPCity.record_by_addr(ip)
        if city:
            return jsonify(city)
        else:
            return jsonify({"error": "IP address not found"}), 404
    except ValueError as e:
        logging.error("ValueError occurred: %s", str(e))
        return jsonify({"error": "Invalid value provided"}), 400
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route(rule='/admin/ban-list', methods=['GET'])
def get_banned_ips():
    """
    Lấy danh sách IP bị cấm
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: Token xác thực admin
    responses:
      200:
        description: Trả về danh sách IP bị cấm
      401:
        description: Thiếu hoặc sai token
    tags:
      - "Admin"
    """
    token = request.args.get('token')
    if not token or not validate_admin_token(token):
        return okResult(isSuccess=False, message="Invalid or missing token", http_code=401)

    ban_list = get_ban_list()
    return okResult(isSuccess=True, message="Ban list retrieved", payload=ban_list, http_code=200)


@app.route(rule='/admin/ban', methods=['POST'])
def add_banned_ip():
    """
    Thêm IP vào danh sách cấm
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: Token xác thực admin
      - name: ip
        in: query
        type: string
        required: true
        description: Địa chỉ IP cần cấm
      - name: reason
        in: query
        type: string
        required: false
        description: Lý do cấm
    responses:
      200:
        description: IP đã được thêm vào danh sách cấm
      400:
        description: Thiếu IP
      401:
        description: Thiếu token
    tags:
      - "Admin"
    """
    token = request.args.get('token')
    if not token or not validate_admin_token(token):
        return okResult(isSuccess=False, message="Invalid or missing token", http_code=401)

    ip = request.args.get('ip')
    if not ip:
        return okResult(isSuccess=False, message="Missing IP address", http_code=400)

    reason = request.args.get('reason', 'Manual ban by admin')
    success = ban_ip(ip, reason)

    if success:
        return okResult(isSuccess=True, message=f"IP {ip} has been banned", http_code=200)
    else:
        return okResult(isSuccess=False, message="Failed to ban IP", http_code=500)


@app.route(rule='/admin/unban', methods=['POST'])
def remove_banned_ip():
    """
    Xóa IP khỏi danh sách cấm
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: Token xác thực admin
      - name: ip
        in: query
        type: string
        required: true
        description: Địa chỉ IP cần bỏ cấm
    responses:
      200:
        description: IP đã được xóa khỏi danh sách cấm
      400:
        description: Thiếu IP
      401:
        description: Thiếu token
      404:
        description: IP không có trong danh sách cấm
    tags:
      - "Admin"
    """
    token = request.args.get('token')
    if not token or not validate_admin_token(token):
        return okResult(isSuccess=False, message="Invalid or missing token", http_code=401)

    ip = request.args.get('ip')
    if not ip:
        return okResult(isSuccess=False, message="Missing IP address", http_code=400)

    success = unban_ip(ip)

    if success:
        return okResult(isSuccess=True, message=f"IP {ip} has been unbanned", http_code=200)
    else:
        return okResult(isSuccess=False, message="IP not found in ban list", http_code=404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
