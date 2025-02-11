from flask import jsonify


def okResult(isSuccess: bool, message: str, payload: object = {}, error: str = ''):
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
        }), 200

    return jsonify({
        "code": -9999,
        "message": message,
        "payload": payload,
        "error": error,
    }), 500
