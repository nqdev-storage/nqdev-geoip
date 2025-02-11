from flask import Blueprint, request, jsonify
import instaloader
from utils.response_helper import okResult

instagram_bp = Blueprint('instagram', __name__, url_prefix='/instagram')


@instagram_bp.route('/getinfo', methods=['GET'])
# https://instaloader.github.io/installation.html
def getinfo_instagram():
    """
    Lấy thông tin tài khoản Instagram
    ---
    parameters:
      - name: username
        in: query
        type: string
        required: true
        description: Tên người dùng Instagram cần tra cứu
    responses:
      200:
        description: Trả về thông tin tài khoản Instagram
        schema:
          type: object
      400:
        description: Thiếu username
      404:
        description: Không tìm thấy tài khoản
      500:
        description: Lỗi server
    """
    username = request.args.get('username')
    if not username:
        return okResult(isSuccess=False, message="Missing Username", error="Missing Username")

    loader = instaloader.Instaloader()

    try:
        # Load the profile
        profile = instaloader.Profile.from_username(
            context=loader.context, username=username)

        # Create a structured object for the profile
        profile_data = {
            "full_name": profile.full_name,
            "userid": profile.userid,
            "username": profile.username,
            "followers": profile.followers,
            "followees": profile.followees,
            "mediacount": profile.mediacount,
            "biography": profile.biography,
            "biography_mentions": profile.biography_mentions,
            "external_url": profile.external_url,
            "is_verified": profile.is_verified,
            "is_private": profile.is_private,
            "followed_by_viewer": profile.followed_by_viewer,
            "blocked_by_viewer": profile.blocked_by_viewer,
            "follows_viewer": profile.follows_viewer,
            "igtvcount": profile.igtvcount,
            "is_business_account": profile.is_business_account,
            "business_category_name": profile.business_category_name,
            "biography_hashtags": profile.biography_hashtags,
            "has_blocked_viewer": profile.has_blocked_viewer,
            "has_highlight_reels": profile.has_highlight_reels,
            "has_public_story": profile.has_public_story,
            "has_viewable_story": profile.has_viewable_story,
            "has_requested_viewer": profile.has_requested_viewer,
            "requested_by_viewer": profile.requested_by_viewer,
            "profile_pic_url": profile.profile_pic_url,
            "profile_pic_url_no_iphone": profile.profile_pic_url_no_iphone,
        }

        # Return the profile object with posts
        return okResult(isSuccess=True, message="success", payload=profile_data)

    except instaloader.exceptions.ProfileNotExistsException as e:
        return okResult(isSuccess=False, message="Không tìm thấy tài khoản!", error=str(e))

    except instaloader.exceptions.ConnectionException as e:
        return okResult(isSuccess=False, message="Không thể kết nối tới Instagram!", error=str(e))

    except Exception as e:
        return okResult(isSuccess=False, message="Exception", error=str(e))
