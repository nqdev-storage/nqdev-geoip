import unittest
import json
from geoip_proxy import app  # Import app từ ứng dụng Flask chính
from unittest.mock import patch
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

# Cấu hình logger
log_filename = f"logs/test_geoip_proxy_{datetime.datetime.now().strftime('%Y%m%d')}.log"
logger = logging.getLogger(__name__)
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


class InstagramRoutesTestCase(unittest.TestCase):
    """Test các route liên quan đến Instagram"""

    def setUp(self):
        """Setup test client trước mỗi test case"""
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        """Ghi log nếu test fail"""
        outcome = self._outcome  # Kết quả của test case

        # Kiểm tra nếu có lỗi hoặc thất bại
        try:
            for test, exc_info in outcome.errors + outcome.failures:
                if exc_info is not None:  # Nếu có lỗi
                    logger.error(f"❌ Test {test.id()} FAILED:\n{exc_info}")
        except Exception as e:
            logger.error(
                f"❌ Test {self._testMethodName} FAILED: {str(e)}", exc_info=True)

    def test_getinfo_missing_username(self):
        """Kiểm tra lỗi khi thiếu username"""
        try:
            response = self.app.get('/instagram/getinfo')
            # API nên trả về 400 Bad Request
            self.assertEqual(response.status_code, 400)

            # Kiểm tra nếu API trả về JSON thay vì text đơn giản
            json_data = response.get_json()
            self.assertIsNotNone(json_data, "Response không phải JSON!")
            self.assertEqual(json_data["message"], "Missing Username")

        except Exception as e:
            logger.error(
                f"❌ Test {self._testMethodName} FAILED: {str(e)}", exc_info=True)
            raise  # Ném lại lỗi để unittest báo thất bại

    # @patch('instaloader.Profile.from_username')
    # def test_getinfo_valid_username(self, mock_instaloader):
    #     """Kiểm tra khi username hợp lệ"""
    #     mock_instaloader.return_value = {
    #         "full_name": "John Doe",
    #         "username": "johndoe",
    #         "followers": 1000,
    #         "followees": 200,
    #         "biography": "This is a test bio",
    #         "is_verified": False
    #     }

    #     response = self.app.get('/instagram/getinfo?username=johndoe')
    #     self.assertEqual(response.status_code, 200)
    #     json_data = response.get_json()
    #     self.assertEqual(json_data["code"], 9999)
    #     self.assertEqual(json_data["payload"]["username"], "johndoe")

    # @patch('instaloader.Profile.from_username')
    # def test_getinfo_invalid_username(self, mock_instaloader):
    #     """Kiểm tra lỗi khi username không tồn tại"""
    #     mock_instaloader.side_effect = Exception("ProfileNotExistsException")

    #     response = self.app.get('/instagram/getinfo?username=invaliduser')
    #     self.assertEqual(response.status_code, 500)
    #     self.assertIn("Exception", response.data.decode())


if __name__ == '__main__':
    unittest.main()
