from flask import Blueprint
from utils.response_helper import okResult

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/<username>', methods=['GET'])
def profile(username):
    return okResult(True, "Lấy thông tin user thành công", {"username": username})
