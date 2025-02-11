from flask import Flask, request, jsonify, url_for
from routes.instagram_routes import instagram_bp
from routes.user_routes import user_bp
import pygeoip
import instaloader
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

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
            # suffix='%Y-%m-%d.log'   # Thêm phần đuôi `.log` và ngày vào tên file
        )
    ]
)

# https://flask.palletsprojects.com/en/stable/
app = Flask(__name__)

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


def okResult(isSuccess: bool, message: str, payload: object = {}, error: str = ''):
    if isSuccess:
        return jsonify({
            "code": 9999,
            "message": message,
            "payload": payload,
        }), 200

    return jsonify({
        "code": -9999,
        "message": message,
        "payload": payload,
        "error": error,
    }), 500


@app.route(rule='/', methods=['GET'])
def home():
    return "Welcome to Flask!"


@app.route(rule='/login')
def login():
    return 'login'


@app.route(rule='/geoip-update', methods=['GET'])
def get_geoip_update():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Missing Token"}), 400

    # Lấy thông tin địa lý từ địa chỉ IP
    try:
        return jsonify({"error": "IP address not found"}), 404
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route(rule='/geoip', methods=['GET'])
def get_geoip_info():
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
        logging.error("Exception occurred", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
