from flask import Flask, request, jsonify, url_for
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


@app.route(rule='/user/<username>')
def profile(username):
    return f'{username}\'s profile'


@app.route(rule='/geoip-update', methods=['GET'])
def get_geoip_update():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Missing Token"}), 400

    # Lấy thông tin địa lý từ địa chỉ IP
    try:
        return jsonify({"error": "IP address not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": "Internal server error: " + str(e)}), 500


@app.route(rule='/instagram/getinfo', methods=['GET'])
# https://instaloader.github.io/installation.html
def getinfo_instagram():
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "Missing Username"}), 400

    loader = instaloader.Instaloader()

    try:
        # Load the profile
        profile = instaloader.Profile.from_username(
            context=loader.context, username=username)

        # Create a structured object for the profile
        profile_data = {
            "full_name": profile.full_name,
            "userid": profile.userid,
            "username": profile.username,
            "followers": profile.followers,
            "followees": profile.followees,
            "mediacount": profile.mediacount,
            "biography": profile.biography,
            "biography_mentions": profile.biography_mentions,
            "external_url": profile.external_url,
            "is_verified": profile.is_verified,
            "is_private": profile.is_private,
            "followed_by_viewer": profile.followed_by_viewer,
            "blocked_by_viewer": profile.blocked_by_viewer,
            "follows_viewer": profile.follows_viewer,
            "igtvcount": profile.igtvcount,
            "is_business_account": profile.is_business_account,
            "business_category_name": profile.business_category_name,
            "biography_hashtags": profile.biography_hashtags,
            "has_blocked_viewer": profile.has_blocked_viewer,
            "has_highlight_reels": profile.has_highlight_reels,
            "has_public_story": profile.has_public_story,
            "has_viewable_story": profile.has_viewable_story,
            "has_requested_viewer": profile.has_requested_viewer,
            "requested_by_viewer": profile.requested_by_viewer,
            "profile_pic_url": profile.profile_pic_url,
            "profile_pic_url_no_iphone": profile.profile_pic_url_no_iphone,
        }

        # Return the profile object with posts
        return okResult(isSuccess=True, message="success", payload=profile_data)
        # return jsonify(profile_data), 200
    except instaloader.exceptions.ProfileNotExistsException as e:
        return okResult(isSuccess=False, message="Không tìm thấy tài khoản!", error=str(e))
    except instaloader.exceptions.ConnectionException as e:
        return okResult(isSuccess=False, message="Không thể kết nối tới Instagram!", error=str(e))
    except Exception as e:
        return okResult(isSuccess=False, message="Exception", error=str(e))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
