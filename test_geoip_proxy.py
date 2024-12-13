import unittest
from geoip_proxy import app  # Giả sử tên ứng dụng của bạn là geoip_proxy.py
from unittest.mock import patch


class GeoIPTestCase(unittest.TestCase):
    # Tạo test client từ Flask
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Kiểm tra route '/'
    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Welcome to Flask!")

    # Kiểm tra route '/login'
    def test_login(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "login")

    # Kiểm tra route '/user/<username>'
    def test_profile(self):
        response = self.app.get('/user/John')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "John's profile")

    # Kiểm tra route '/geoip' khi thiếu IP
    def test_geoip_missing_ip(self):
        response = self.app.get('/geoip?token=some_token')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing IP address", response.data.decode())

    # Kiểm tra route '/geoip' với IP hợp lệ
    @patch('pygeoip.GeoIP.country_code_by_addr', return_value='US')
    def test_geoip_valid_ip(self, mock_geoip):
        response = self.app.get('/geoip?ip=8.8.8.8&token=some_token')
        self.assertEqual(response.status_code, 200)
        self.assertIn("country", response.json)
        self.assertEqual(response.json["country"], "US")

    # Kiểm tra route '/geoip' với IP không hợp lệ
    @patch('pygeoip.GeoIP.country_code_by_addr', return_value=None)
    def test_geoip_invalid_ip(self, mock_geoip):
        response = self.app.get('/geoip?ip=0.0.0.0&token=some_token')
        self.assertEqual(response.status_code, 404)
        self.assertIn("IP address not found", response.data.decode())

    # Kiểm tra route '/geoipcity' khi thiếu IP
    def test_geoipcity_missing_ip(self):
        response = self.app.get('/geoipcity?token=some_token')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing IP address", response.data.decode())

    # Kiểm tra route '/geoipcity' với IP hợp lệ
    @patch('pygeoip.GeoIP.record_by_addr', return_value={'city': 'Mountain View', 'country_code': 'US'})
    def test_geoipcity_valid_ip(self, mock_geoipcity):
        response = self.app.get('/geoipcity?ip=8.8.8.8&token=some_token')
        self.assertEqual(response.status_code, 200)
        self.assertIn("city", response.json)
        self.assertEqual(response.json["city"], "Mountain View")

    # Kiểm tra route '/geoipcity' với IP không hợp lệ
    @patch('pygeoip.GeoIP.record_by_addr', return_value=None)
    def test_geoipcity_invalid_ip(self, mock_geoipcity):
        response = self.app.get('/geoipcity?ip=0.0.0.0&token=some_token')
        self.assertEqual(response.status_code, 404)
        self.assertIn("IP address not found", response.data.decode())

    # Kiểm tra route '/geoip-update' khi thiếu token
    def test_geoip_update_missing_token(self):
        response = self.app.get('/geoip-update')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing Token", response.data.decode())

    # Kiểm tra route '/geoip-update' khi có token nhưng không có IP
    @patch('pygeoip.GeoIP.country_code_by_addr', return_value='US')
    def test_geoip_update_with_token(self, mock_geoip):
        response = self.app.get('/geoip-update?token=some_token&ip=8.8.8.8')
        self.assertEqual(response.status_code, 404)
        self.assertIn("IP address not found", response.data.decode())


if __name__ == '__main__':
    unittest.main()
