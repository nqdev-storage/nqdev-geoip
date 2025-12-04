from flask import Flask, request, jsonify
from flasgger import Swagger
from werkzeug.middleware.proxy_fix import ProxyFix
import pygeoip
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

from routes.ip2location_routes import ip2location_bp
from routes.user_routes import user_bp
from routes.admin.ban_routes import admin_ban_bp, ADMIN_ENDPOINTS

from config import Config
from geoip_update import download_and_extract, url_geoip, url_geoip_city
from utils.response_helper import okResult
from utils.ip_ban import (
    is_ip_banned, ban_ip, unban_ip,
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
app.register_blueprint(admin_ban_bp)

# Tải tệp GeoIP for V2Ray
# Thay đổi đường dẫn tới tệp `.dat` của bạn
GeoIP_path = './dbs/GeoIP.dat'
geoip = pygeoip.GeoIP(GeoIP_path)

# Tải tệp GeoIPCity cho V2Ray
GeoIPCity_path = './dbs/GeoIPCity.dat'
GeoIPCity = pygeoip.GeoIP(GeoIPCity_path)


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

if __name__ == '__main__':
    # Log thông tin về việc khởi động server trong môi trường sản xuất
    print(f'Version: {__version__}')
    print(f'ApiDocs on http://localhost:5000/apidocs/')
    print('Starting Flask development server on http://localhost:5000')
    print(f'Admin token: {Config.ADMIN_TOKEN}')

    app.run(host='0.0.0.0', port=5000, debug=False)
