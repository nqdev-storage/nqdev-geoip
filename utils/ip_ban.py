"""
IP Ban utility module for blocking suspicious/malicious IPs.
Provides functionality to manage a ban list stored in a JSON file.
"""
import json
import os
import re
import datetime
import logging
from typing import Dict, List

# File paths
BAN_LIST_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'dbs', 'banned_ips.json')
SUSPICIOUS_PATTERNS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'dbs', 'suspicious.txt')


def _load_suspicious_patterns() -> List[str]:
    """Load suspicious URL patterns from file."""
    patterns = []
    if not os.path.exists(SUSPICIOUS_PATTERNS_FILE):
        logging.warning(
            f"Suspicious patterns file not found: {SUSPICIOUS_PATTERNS_FILE}")
        return [
            r'/vtigercrm',
            r'/wp-admin',
            r'/wp-login',
            r'/phpMyAdmin',
            r'/phpmyadmin',
            r'/admin\.php',
            r'/shell\.php',
            r'/\.env',
            r'/\.git',
            r'/config\.php',
            r'/xmlrpc\.php',
            r'/wp-content',
            r'/wp-includes',
            r'/cgi-bin',
            r'/manager/html',
            r'/solr',
            r'/actuator',
            r'/api/v1/pods',
            r'/login\.action',
            r'/console',
            r'/debug',
            r'/trace',
            r'passwd',
            # Path traversal attacks (URL encoded and plain)
            r'\.\./',                      # Plain path traversal
            r'\.\.%2[fF]',                 # URL encoded ../ (..%2F)
            r'%2[eE]%2[eE]%2[fF]',         # URL encoded ../ (%2E%2E%2F)
            r'/etc/passwd',                # Direct /etc/passwd access
            r'/etc/shadow',                # Direct /etc/shadow access
            # PHP file scanning patterns (common vulnerable PHP apps)
            r'/a2billing',                 # a2billing VoIP billing
            r'/roundcube',                 # Roundcube webmail
            r'/webmail',                   # Generic webmail
            r'/cpanel',                    # cPanel
            r'/plesk',                     # Plesk
            r'/joomla',                    # Joomla CMS
            r'/drupal',                    # Drupal CMS
            r'/magento',                   # Magento e-commerce
            r'/typo3',                     # TYPO3 CMS
            r'/myadmin',                   # MySQL admin
            r'/pma',                       # phpMyAdmin alias
            r'/adminer',                   # Adminer database tool
            r'/owa',                       # Outlook Web Access
            # General PHP file pattern (any .php file access)
            r'\.php$',                     # Any .php file at end of path
            r'\.php\?',                    # Any .php file with query string
            r'\.php/',                     # Any .php file with trailing path
        ]

    try:
        with open(SUSPICIOUS_PATTERNS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    patterns.append(line)
    except IOError as e:
        logging.error(f"Error loading suspicious patterns: {e}")

    return patterns


# Load and compile patterns
SUSPICIOUS_PATTERNS = _load_suspicious_patterns()
COMPILED_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in SUSPICIOUS_PATTERNS]


def _load_ban_list() -> Dict:
    """Load the ban list from JSON file."""
    if not os.path.exists(BAN_LIST_FILE):
        return {"banned_ips": {}}
    try:
        with open(BAN_LIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error loading ban list: {e}")
        return {"banned_ips": {}}


def _save_ban_list(data: Dict) -> bool:
    """Save the ban list to JSON file."""
    try:
        os.makedirs(os.path.dirname(BAN_LIST_FILE), exist_ok=True)
        with open(BAN_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logging.error(f"Error saving ban list: {e}")
        return False


def is_ip_banned(ip: str) -> bool:
    """Check if an IP is in the ban list."""
    data = _load_ban_list()
    return ip in data.get("banned_ips", {})


def ban_ip(ip: str, reason: str = "Suspicious request") -> bool:
    """
    Add an IP to the ban list.

    Args:
        ip: The IP address to ban
        reason: The reason for banning

    Returns:
        True if successfully banned, False otherwise
    """
    data = _load_ban_list()
    if "banned_ips" not in data:
        data["banned_ips"] = {}

    data["banned_ips"][ip] = {
        "reason": reason,
        "banned_at": datetime.datetime.now().isoformat(),
    }

    logging.warning(f"IP {ip} banned. Reason: {reason}")
    return _save_ban_list(data)


def unban_ip(ip: str) -> bool:
    """
    Remove an IP from the ban list.

    Args:
        ip: The IP address to unban

    Returns:
        True if successfully unbanned, False otherwise
    """
    data = _load_ban_list()
    if ip in data.get("banned_ips", {}):
        del data["banned_ips"][ip]
        logging.info(f"IP {ip} unbanned.")
        return _save_ban_list(data)
    return False


def get_ban_list() -> Dict:
    """Get the full ban list."""
    return _load_ban_list().get("banned_ips", {})


def is_suspicious_request(path: str) -> bool:
    """
    Check if a request path matches any suspicious patterns.

    Args:
        path: The request path to check

    Returns:
        True if the path matches a suspicious pattern
    """
    for pattern in COMPILED_PATTERNS:
        if pattern.search(path):
            return True
    return False


def get_client_ip(request) -> str:
    """
    Get the real client IP from a Flask request, handling proxies.

    Note: X-Forwarded-For header is trusted as the app runs behind ProxyFix
    middleware which handles proxy trust appropriately.

    Args:
        request: Flask request object

    Returns:
        The client IP address
    """
    # Fall back to remote_addr first (ProxyFix handles X-Forwarded-For)
    if request.remote_addr:
        return request.remote_addr

    # If remote_addr is not available, check headers as fallback
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # Get the first IP in the chain (client IP)
        return forwarded_for.split(',')[0].strip()

    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip.strip()

    # Return 'unknown' if no IP can be determined
    return 'unknown'
