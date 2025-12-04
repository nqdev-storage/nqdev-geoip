from flask import Blueprint
from utils.response_helper import okResult, errorResult

# Create a blueprint for user-related routes
user_bp = Blueprint(name='user',
                    import_name=__name__,
                    url_prefix='/user')


@user_bp.route('/<username>', methods=['GET'])
def profile(username):
    """
    Lấy thông tin người dùng dựa trên tên người dùng được cung cấp
    ---
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: Tên người dùng
    responses:
      200:
        description: Successfully retrieved user information.
        schema:
          type: object
          properties:
            username:
              type: string
            details:
              type: object
      404:
        description: User not found.
        schema:
          type: object
          properties:
            message:
              type: string
            error_code:
              type: integer
        examples:
          application/json:
            message: "Không tìm thấy người dùng"
            error_code: 404
    tags:
      - "User"
    """
    # For demonstration, let's pretend we check a database for the username
    user_data = get_user_data(username)  # This would be a database call

    if user_data:
        return okResult(True, "Lấy thông tin user thành công", {"username": username, "details": user_data})
    else:
        return errorResult(False, "Không tìm thấy người dùng", status_code=404)


def get_user_data(username):
    """
    A placeholder function to simulate checking user data from a database.
    You would replace this with your actual database logic.
    """
    # Example user data (you can replace it with your DB query)
    example_user_data = {
        "john": {"name": "John Doe", "email": "john@example.com", "age": 30},
        "jane": {"name": "Jane Doe", "email": "jane@example.com", "age": 25},
    }

    return example_user_data.get(username)
