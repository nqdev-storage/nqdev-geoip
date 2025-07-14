import unittest
from geoip_proxy import app  # Giả sử tên ứng dụng của bạn là geoip_proxy.py
from unittest.mock import patch
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

# Cấu hình logger
log_filename = f"logs/test_geoip_proxy_{datetime.datetime.now().strftime('%Y%m%d')}.log"
logger = logging.getLogger("GeoIPTestLogger")
logger.setLevel(logging.DEBUG)

# Xóa handler cũ (tránh log trùng khi chạy nhiều lần)
if logger.hasHandlers():
    logger.handlers.clear()

# Thêm handler cho console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Thêm handler cho file
file_handler = TimedRotatingFileHandler(
    filename=log_filename,
    when="midnight",  # Tạo file log mới mỗi ngày
    interval=1,
    backupCount=7,  # Giữ log tối đa 7 ngày
    encoding="utf-8",
)

# Định dạng log
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Gắn handler vào logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


class GeoIPTestCase(unittest.TestCase):
    """Test các route liên quan đến GeoIP"""

    @classmethod
    def setUpClass(cls):
        """Chạy 1 lần duy nhất trước tất cả test cases."""
        logger.info("Bắt đầu chạy test suite GeoIPTestCase.")

    @classmethod
    def tearDownClass(cls):
        """Chạy 1 lần duy nhất sau tất cả test cases."""
        logger.info("Hoàn thành test suite GeoIPTestCase.")

    # Tạo test client từ Flask
    def setUp(self):
        """Chạy trước mỗi test case."""
        self.app = app.test_client()
        self.app.testing = True
        self.test_name = self._testMethodName  # Lưu tên test case hiện tại
        logger.info(f"Bắt đầu test: {self._testMethodName}")

    def log_failure(self, error):
        """ Ghi log khi test thất bại """
        logger.error(f"❌ Test FAILED: {self.test_name} - Error: {error}")

    def addCleanup(self):
        """ Kiểm tra nếu test thất bại thì ghi log """
        result = self._outcome.result
        if result.failures or result.errors:
            for test_case, error in result.failures + result.errors:
                if test_case is self:
                    self.log_failure(error)

    def tearDown(self):
        """Chạy sau mỗi test case."""
        logger.info(f"Hoàn thành test: {self._testMethodName}")

    # Kiểm tra route '/'
    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Welcome to Flask!")

    # Kiểm tra route '/login'
    # def test_login(self):
    #     response = self.app.get('/login')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data.decode(), "login")

    # Kiểm tra route '/user/<username>'
    # def test_profile(self):
    #     response = self.app.get('/user/John')
    #     self.assertEqual(response.status_code, 200)
    #     # Parse JSON để kiểm tra nội dung
    #     json_data = response.get_json()
    #     self.assertEqual(json_data["code"], 9999)
    #     self.assertEqual(json_data["payload"]["username"], "John")

    # Kiểm tra route '/geoip' khi thiếu IP
    # def test_geoip_missing_ip(self):
    #     response = self.app.get('/geoip?token=some_token')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn("Missing IP address", response.data.decode())

    # Kiểm tra route '/geoip' với IP hợp lệ
    # @patch('pygeoip.GeoIP.country_code_by_addr', return_value='US')
    # def test_geoip_valid_ip(self, mock_geoip):
    #     response = self.app.get('/geoip?ip=8.8.8.8&token=some_token')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn("country", response.json)
    #     self.assertEqual(response.json["country"], "US")

    # Kiểm tra route '/geoip' với IP không hợp lệ
    # @patch('pygeoip.GeoIP.country_code_by_addr', return_value=None)
    # def test_geoip_invalid_ip(self, mock_geoip):
    #     response = self.app.get('/geoip?ip=0.0.0.0&token=some_token')
    #     self.assertEqual(response.status_code, 404)
    #     self.assertIn("IP address not found", response.data.decode())

    # Kiểm tra route '/geoipcity' khi thiếu IP
    # def test_geoipcity_missing_ip(self):
    #     response = self.app.get('/geoipcity?token=some_token')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn("Missing IP address", response.data.decode())

    # Kiểm tra route '/geoipcity' với IP hợp lệ
    # @patch('pygeoip.GeoIP.record_by_addr', return_value={'city': 'Mountain View', 'country_code': 'US'})
    # def test_geoipcity_valid_ip(self, mock_geoipcity):
    #     response = self.app.get('/geoipcity?ip=8.8.8.8&token=some_token')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn("city", response.json)
    #     self.assertEqual(response.json["city"], "Mountain View")

    # Kiểm tra route '/geoipcity' với IP không hợp lệ
    # @patch('pygeoip.GeoIP.record_by_addr', return_value=None)
    # def test_geoipcity_invalid_ip(self, mock_geoipcity):
    #     response = self.app.get('/geoipcity?ip=0.0.0.0&token=some_token')
    #     self.assertEqual(response.status_code, 404)
    #     self.assertIn("IP address not found", response.data.decode())

    # Kiểm tra route '/geoip-update' khi thiếu token
    # def test_geoip_update_missing_token(self):
    #     response = self.app.get('/geoip-update')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn("Missing Token", response.data.decode())

    # Kiểm tra route '/geoip-update' khi có token nhưng không có IP
    # @patch('pygeoip.GeoIP.country_code_by_addr', return_value='US')
    # def test_geoip_update_with_token(self, mock_geoip):
    #     response = self.app.get('/geoip-update?token=some_token&ip=8.8.8.8')
    #     self.assertEqual(response.status_code, 404)
    #     self.assertIn("IP address not found", response.data.decode())


if __name__ == "__main__":
    try:
        unittest.main()
    except Exception as e:
        logger.error(f"Lỗi khi chạy test: {e}")
