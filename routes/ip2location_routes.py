from flask import Blueprint
from utils.response_helper import okResult, errorResult

# Create a blueprint for user-related routes
ip2location_bp = Blueprint(name='ip2location',
                           import_name=__name__,
                           url_prefix='/ip2location')


@ip2location_bp.route('/download/<db_code>', methods=['GET'])
def download(db_code):
    """
    Tải tệp IP2Location dựa trên mã cơ sở dữ liệu được cung cấp
    ---
    parameters:
      - name: db_code
        in: path
        type: string
        required: true
        description: Mã cơ sở dữ liệu IP2Location
    responses:
      200:
        description: Successfully retrieved the IP2Location database.
    tags:
      - "IP2Location"
    """
    return okResult(True, "Lấy thông tin user thành công", {"db_code": db_code})
