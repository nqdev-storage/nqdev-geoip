import unittest
from utils.private_cidr import (
    is_private_cidr, get_private_cidr_response, get_private_cidr_country_code
)


class PrivateCIDRTestCase(unittest.TestCase):
    """Test các chức năng Private CIDR"""

    def test_is_private_cidr_10_network(self):
        """Kiểm tra IP trong dải 10.0.0.0/8"""
        self.assertTrue(is_private_cidr("10.0.0.1"))
        self.assertTrue(is_private_cidr("10.255.255.255"))
        self.assertTrue(is_private_cidr("10.128.64.32"))

    def test_is_private_cidr_172_network(self):
        """Kiểm tra IP trong dải 172.16.0.0/12"""
        self.assertTrue(is_private_cidr("172.16.0.1"))
        self.assertTrue(is_private_cidr("172.31.255.255"))
        self.assertTrue(is_private_cidr("172.20.10.5"))

    def test_is_private_cidr_192_network(self):
        """Kiểm tra IP trong dải 192.168.0.0/16"""
        self.assertTrue(is_private_cidr("192.168.0.1"))
        self.assertTrue(is_private_cidr("192.168.255.255"))
        self.assertTrue(is_private_cidr("192.168.2.100"))

    def test_is_private_cidr_public_ip(self):
        """Kiểm tra IP công cộng không thuộc dải private"""
        self.assertFalse(is_private_cidr("8.8.8.8"))
        self.assertFalse(is_private_cidr("1.1.1.1"))
        self.assertFalse(is_private_cidr("203.113.152.1"))

    def test_is_private_cidr_invalid_ip(self):
        """Kiểm tra xử lý IP không hợp lệ"""
        self.assertFalse(is_private_cidr("invalid_ip"))
        self.assertFalse(is_private_cidr("256.256.256.256"))
        self.assertFalse(is_private_cidr(""))

    def test_get_private_cidr_response(self):
        """Kiểm tra lấy response mặc định"""
        response = get_private_cidr_response()
        self.assertIsNotNone(response)
        self.assertIn("country_code", response)
        self.assertEqual(response["country_code"], "VN")
        self.assertIn("country_name", response)
        self.assertEqual(response["country_name"], "Vietnam")

    def test_get_private_cidr_country_code(self):
        """Kiểm tra lấy country code mặc định"""
        country_code = get_private_cidr_country_code()
        self.assertEqual(country_code, "VN")


class PrivateCIDRIntegrationTestCase(unittest.TestCase):
    """Test tích hợp Private CIDR trong geoip_proxy"""

    def setUp(self):
        """Setup trước mỗi test case"""
        from geoip_proxy import app
        self.app = app.test_client()
        self.app.testing = True

    def test_geoip_private_ip(self):
        """Kiểm tra /geoip với IP private"""
        response = self.app.get('/geoip?ip=192.168.1.100')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("country", data)
        self.assertEqual(data["country"], "VN")

    def test_geoip_10_network_ip(self):
        """Kiểm tra /geoip với IP trong dải 10.x.x.x"""
        response = self.app.get('/geoip?ip=10.0.0.1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("country", data)
        self.assertEqual(data["country"], "VN")

    def test_geoipcity_private_ip(self):
        """Kiểm tra /geoipcity với IP private"""
        response = self.app.get('/geoipcity?ip=192.168.2.100')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("country_code", data)
        self.assertEqual(data["country_code"], "VN")
        self.assertIn("country_name", data)
        self.assertEqual(data["country_name"], "Vietnam")
        self.assertIn("latitude", data)
        self.assertIn("longitude", data)

    def test_geoipcity_172_network_ip(self):
        """Kiểm tra /geoipcity với IP trong dải 172.16.x.x"""
        response = self.app.get('/geoipcity?ip=172.16.0.1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("country_code", data)
        self.assertEqual(data["country_code"], "VN")


if __name__ == '__main__':
    unittest.main()
