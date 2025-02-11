from waitress import serve
from geoip_proxy import app  # Giả sử ứng dụng Flask của bạn là 'app'

print(f'ApiDocs on http://localhost:5000/apidocs/')
serve(app=app, host='0.0.0.0', port=5000)
