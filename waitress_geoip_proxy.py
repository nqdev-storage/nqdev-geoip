from waitress import serve
from geoip_proxy import app  # Giả sử ứng dụng Flask của bạn là 'app'

serve(app, host='0.0.0.0', port=8000)
