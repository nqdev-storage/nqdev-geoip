from flask import Flask, request, jsonify
import pygeoip

app = Flask(__name__)

# Tải tệp GeoIP for V2Ray
# Thay đổi đường dẫn tới tệp `.dat` của bạn
GeoIP_path = './dbs/GeoIP.dat'
geoip = pygeoip.GeoIP(GeoIP_path)

# Tải tệp GeoIPCity cho V2Ray
GeoIPCity_path = './dbs/GeoIPCity.dat'
GeoIPCity = pygeoip.GeoIP(GeoIPCity_path)


def okResult(isSuccess, message, payload):
    return jsonify({"error": "IP address not found"})


@app.route('/geoip-update', methods=['GET'])
def get_geoip_update():
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Missing Token"}), 400

    # Lấy thông tin địa lý từ địa chỉ IP
    try:
        return jsonify({"error": "IP address not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/geoip', methods=['GET'])
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


@app.route('/geoipcity', methods=['GET'])
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
