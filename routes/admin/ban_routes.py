from flask import Flask, Blueprint, request, jsonify, url_for

from config import Config
from utils.response_helper import okResult, errorResult
from utils.ip_ban import (
    is_ip_banned, ban_ip, unban_ip, get_ban_list,
    is_suspicious_request, get_client_ip
)

# Create a blueprint for user-related routes
admin_ban_bp = Blueprint(name='admin_ban', import_name=__name__,
                         url_prefix='/admin/ban')


# Admin endpoints exempt from IP ban checks
ADMIN_ENDPOINTS = ['/admin/ban/list', '/admin/ban/add', '/admin/ban/unban']


def validate_admin_token(token: str) -> bool:
    """Validate admin token against configured value."""
    expected_token = Config.ADMIN_TOKEN
    return token == expected_token


@admin_ban_bp.route(rule='/list', methods=['GET'])
def get_banned_ips():
    """
    Lấy danh sách IP bị cấm
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: Token xác thực admin
    responses:
      200:
        description: Trả về danh sách IP bị cấm
      401:
        description: Thiếu hoặc sai token
    tags:
      - "Admin"
    """
    token = request.args.get('token')
    if not token or not validate_admin_token(token):
        return okResult(isSuccess=False, message="Invalid or missing token", http_code=401)

    ban_list = get_ban_list()
    return okResult(isSuccess=True, message="Ban list retrieved", payload=ban_list, http_code=200)


@admin_ban_bp.route(rule='/add', methods=['POST'])
def add_banned_ip():
    """
    Thêm IP vào danh sách cấm
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: Token xác thực admin
      - name: ip
        in: query
        type: string
        required: true
        description: Địa chỉ IP cần cấm
      - name: reason
        in: query
        type: string
        required: false
        description: Lý do cấm
    responses:
      200:
        description: IP đã được thêm vào danh sách cấm
      400:
        description: Thiếu IP
      401:
        description: Thiếu token
    tags:
      - "Admin"
    """
    token = request.args.get('token')
    if not token or not validate_admin_token(token):
        return okResult(isSuccess=False, message="Invalid or missing token", http_code=401)

    ip = request.args.get('ip')
    if not ip:
        return okResult(isSuccess=False, message="Missing IP address", http_code=400)

    reason = request.args.get('reason', 'Manual ban by admin')
    success = ban_ip(ip, reason)

    if success:
        return okResult(isSuccess=True, message=f"IP {ip} has been banned", http_code=200)
    else:
        return okResult(isSuccess=False, message="Failed to ban IP", http_code=500)


@admin_ban_bp.route(rule='/unban', methods=['POST'])
def remove_banned_ip():
    """
    Xóa IP khỏi danh sách cấm
    ---
    parameters:
      - name: token
        in: query
        type: string
        required: true
        description: Token xác thực admin
      - name: ip
        in: query
        type: string
        required: true
        description: Địa chỉ IP cần bỏ cấm
    responses:
      200:
        description: IP đã được xóa khỏi danh sách cấm
      400:
        description: Thiếu IP
      401:
        description: Thiếu token
      404:
        description: IP không có trong danh sách cấm
    tags:
      - "Admin"
    """
    token = request.args.get('token')
    if not token or not validate_admin_token(token):
        return okResult(isSuccess=False, message="Invalid or missing token", http_code=401)

    ip = request.args.get('ip')
    if not ip:
        return okResult(isSuccess=False, message="Missing IP address", http_code=400)

    success = unban_ip(ip)

    if success:
        return okResult(isSuccess=True, message=f"IP {ip} has been unbanned", http_code=200)
    else:
        return okResult(isSuccess=False, message="IP not found in ban list", http_code=404)
