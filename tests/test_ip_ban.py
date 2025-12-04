import unittest
import os
from unittest.mock import MagicMock
from utils.ip_ban import (
    is_ip_banned, ban_ip, unban_ip, get_ban_list,
    is_suspicious_request, get_client_ip, BAN_LIST_FILE
)


class IPBanTestCase(unittest.TestCase):
    """Test các chức năng IP ban"""

    def setUp(self):
        """Setup trước mỗi test case"""
        # Clear ban list before each test
        if os.path.exists(BAN_LIST_FILE):
            os.remove(BAN_LIST_FILE)

    def tearDown(self):
        """Cleanup sau mỗi test case"""
        # Clean up ban list file
        if os.path.exists(BAN_LIST_FILE):
            os.remove(BAN_LIST_FILE)

    def test_ban_ip(self):
        """Kiểm tra chức năng ban IP"""
        test_ip = "192.168.1.100"
        result = ban_ip(test_ip, "Test ban")
        self.assertTrue(result)
        self.assertTrue(is_ip_banned(test_ip))

    def test_unban_ip(self):
        """Kiểm tra chức năng unban IP"""
        test_ip = "192.168.1.101"
        ban_ip(test_ip, "Test ban")
        self.assertTrue(is_ip_banned(test_ip))

        result = unban_ip(test_ip)
        self.assertTrue(result)
        self.assertFalse(is_ip_banned(test_ip))

    def test_unban_nonexistent_ip(self):
        """Kiểm tra unban IP không tồn tại"""
        result = unban_ip("192.168.1.102")
        self.assertFalse(result)

    def test_get_ban_list(self):
        """Kiểm tra lấy danh sách IP bị ban"""
        ban_ip("192.168.1.103", "Test ban 1")
        ban_ip("192.168.1.104", "Test ban 2")

        ban_list = get_ban_list()
        self.assertIn("192.168.1.103", ban_list)
        self.assertIn("192.168.1.104", ban_list)
        self.assertEqual(len(ban_list), 2)

    def test_is_suspicious_request_vtigercrm(self):
        """Kiểm tra phát hiện request đáng ngờ - vtigercrm"""
        self.assertTrue(is_suspicious_request("/vtigercrm/index.php"))

    def test_is_suspicious_request_wp_admin(self):
        """Kiểm tra phát hiện request đáng ngờ - wp-admin"""
        self.assertTrue(is_suspicious_request("/wp-admin/"))

    def test_is_suspicious_request_phpMyAdmin(self):
        """Kiểm tra phát hiện request đáng ngờ - phpMyAdmin"""
        self.assertTrue(is_suspicious_request("/phpMyAdmin/"))
        self.assertTrue(is_suspicious_request("/phpmyadmin/"))

    def test_is_suspicious_request_shell(self):
        """Kiểm tra phát hiện request đáng ngờ - shell.php"""
        self.assertTrue(is_suspicious_request("/shell.php"))

    def test_is_suspicious_request_env(self):
        """Kiểm tra phát hiện request đáng ngờ - .env"""
        self.assertTrue(is_suspicious_request("/.env"))

    def test_is_suspicious_request_normal(self):
        """Kiểm tra request bình thường không bị phát hiện"""
        self.assertFalse(is_suspicious_request("/"))
        self.assertFalse(is_suspicious_request("/geoip"))
        self.assertFalse(is_suspicious_request("/geoipcity"))
        self.assertFalse(is_suspicious_request("/user/john"))

    def test_get_client_ip_direct(self):
        """Kiểm tra lấy IP client trực tiếp"""
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.remote_addr = "192.168.1.1"

        ip = get_client_ip(mock_request)
        self.assertEqual(ip, "192.168.1.1")

    def test_get_client_ip_forwarded(self):
        """Kiểm tra lấy IP client qua X-Forwarded-For khi remote_addr trống"""
        mock_request = MagicMock()
        mock_request.headers = {"X-Forwarded-For": "10.0.0.1, 10.0.0.2"}
        mock_request.remote_addr = None

        ip = get_client_ip(mock_request)
        self.assertEqual(ip, "10.0.0.1")

    def test_get_client_ip_real_ip(self):
        """Kiểm tra lấy IP client qua X-Real-IP khi remote_addr trống"""
        mock_request = MagicMock()
        mock_request.headers = {"X-Real-IP": "10.0.0.3"}
        mock_request.remote_addr = None

        ip = get_client_ip(mock_request)
        self.assertEqual(ip, "10.0.0.3")

    def test_get_client_ip_unknown(self):
        """Kiểm tra fallback khi không có IP"""
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.remote_addr = None

        ip = get_client_ip(mock_request)
        self.assertEqual(ip, "unknown")


class GeoIPProxyBanTestCase(unittest.TestCase):
    """Test tích hợp IP ban trong geoip_proxy"""

    def setUp(self):
        """Setup trước mỗi test case"""
        # Clear ban list
        if os.path.exists(BAN_LIST_FILE):
            os.remove(BAN_LIST_FILE)

        from geoip_proxy import app
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        """Cleanup sau mỗi test case"""
        if os.path.exists(BAN_LIST_FILE):
            os.remove(BAN_LIST_FILE)

    def test_suspicious_request_banned(self):
        """Kiểm tra request đáng ngờ bị block và ban IP"""
        response = self.app.get('/vtigercrm/index.php')
        self.assertEqual(response.status_code, 403)

    def test_normal_request_allowed(self):
        """Kiểm tra request bình thường được phép"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_admin_get_ban_list(self):
        """Kiểm tra API lấy danh sách ban"""
        # First, ban an IP
        ban_ip("10.0.0.1", "Test")

        # Use the default admin token from config
        response = self.app.get('/admin/ban-list?token=your_admin_token_here')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("10.0.0.1", data["payload"])

    def test_admin_ban_ip(self):
        """Kiểm tra API ban IP"""
        response = self.app.post('/admin/ban?token=your_admin_token_here&ip=10.0.0.2&reason=test')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(is_ip_banned("10.0.0.2"))

    def test_admin_unban_ip(self):
        """Kiểm tra API unban IP"""
        ban_ip("10.0.0.3", "Test")

        response = self.app.post('/admin/unban?token=your_admin_token_here&ip=10.0.0.3')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(is_ip_banned("10.0.0.3"))

    def test_admin_invalid_token(self):
        """Kiểm tra admin API với token không hợp lệ"""
        response = self.app.get('/admin/ban-list?token=invalid_token')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
