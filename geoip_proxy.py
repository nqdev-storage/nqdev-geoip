from flask import Flask, request, jsonify
from flasgger import Swagger
import pygeoip
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

from routes.instagram_routes import instagram_bp
from routes.user_routes import user_bp

from geoip_update import download_and_extract, url_geoip, url_geoip_city

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
Swagger(app=app)    # Khởi tạo Swagger

# Đăng ký route
app.register_blueprint(instagram_bp)
app.register_blueprint(user_bp)

# Tải tệp GeoIP for V2Ray
# Thay đổi đường dẫn tới tệp `.dat` của bạn
GeoIP_path = './dbs/GeoIP.dat'
geoip = pygeoip.GeoIP(GeoIP_path)

# Tải tệp GeoIPCity cho V2Ray
GeoIPCity_path = './dbs/GeoIPCity.dat'
GeoIPCity = pygeoip.GeoIP(GeoIPCity_path)


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
      400:
        description: Thiếu Token
      404:
        description: Không tìm thấy địa chỉ IP
      500:
        description: Lỗi server
    """
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Missing Token"}), 400

    # Lấy thông tin địa lý từ địa chỉ IP
    try:
        download_and_extract(url_geoip, './dbs/GeoIP.dat')
        download_and_extract(url_geoip_city, './dbs/GeoIPCity.dat')

        return jsonify({"error": "IP address not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": "Invalid value: " + str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error: " + str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
