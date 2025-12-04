# import os
from flask import jsonify

# ENV = os.getenv("ENV", "development")  # mặc định là development nếu chưa set


def okResult(isSuccess: bool, message: str, payload: object = {}, error: str = '', http_code: int = -1):
    """
    Hàm trả về response JSON theo cấu trúc chuẩn.

    :param isSuccess: True nếu thành công, False nếu lỗi
    :param message: Thông điệp phản hồi
    :param payload: Dữ liệu trả về (mặc định là object rỗng)
    :param error: Mô tả lỗi nếu có
    :return: Flask Response object
    """
    if isSuccess:
        return jsonify({
            "code": 9999,
            "message": message,
            "payload": payload,
        }), (200 if http_code < 0 else http_code)

    return jsonify({
        "code": -9999,
        "message": message,
        "payload": payload,
        # ẩn lỗi nếu production
        # "error": None if ENV == "production" else error,
    }), (500 if http_code < 0 else http_code)


def errorResult(success, message, status_code=400):
    """
    Standard response for failed requests.
    """
    response = {
        "success": success,
        "message": message,
        "error_code": status_code
    }
    return jsonify(response), status_code
