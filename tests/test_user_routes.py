import unittest
from geoip_proxy import app  # Import app từ ứng dụng Flask chính


class UserRoutesTestCase(unittest.TestCase):
    """Test các route liên quan đến User"""

    def setUp(self):
        """Setup test client trước mỗi test case"""
        self.app = app.test_client()
        self.app.testing = True

    def test_profile(self):
        """Kiểm tra route '/user/<username>' """
        response = self.app.get('/user/john')
        self.assertEqual(response.status_code, 200)

        # Kiểm tra nếu API trả về JSON thay vì text đơn giản
        json_data = response.get_json()
        self.assertEqual(json_data["code"], 9999)
        self.assertEqual(json_data["payload"]["username"], "john")


if __name__ == '__main__':
    unittest.main()
