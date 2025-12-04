"""
Private CIDR utility module.
Provides functionality to check if an IP address falls within configured
private CIDR ranges and return default GeoIP data for such addresses.
"""
import json
import os
import ipaddress
import logging
from typing import Dict, Optional

# Private CIDR config file path
PRIVATE_CIDR_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'dbs',
    'private_cidr_config.json'
)


def _load_private_cidr_config() -> Dict:
    """Load the private CIDR configuration from JSON file."""
    if not os.path.exists(PRIVATE_CIDR_CONFIG_FILE):
        return {"private_cidrs": [], "default_response": {}}
    try:
        with open(PRIVATE_CIDR_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error loading private CIDR config: {e}")
        return {"private_cidrs": [], "default_response": {}}


def is_private_cidr(ip: str) -> bool:
    """
    Check if an IP address falls within any configured private CIDR range.

    Args:
        ip: The IP address to check

    Returns:
        True if the IP is within a private CIDR range, False otherwise
    """
    try:
        config = _load_private_cidr_config()
        ip_obj = ipaddress.ip_address(ip)

        for cidr in config.get("private_cidrs", []):
            network = ipaddress.ip_network(cidr, strict=False)
            if ip_obj in network:
                return True
        return False
    except ValueError as e:
        logging.error(f"Invalid IP address or CIDR: {e}")
        return False


def get_private_cidr_response() -> Optional[Dict]:
    """
    Get the default response for private CIDR addresses.

    Returns:
        The default response dictionary, or None if not configured
    """
    config = _load_private_cidr_config()
    return config.get("default_response")


def get_private_cidr_country_code() -> Optional[str]:
    """
    Get the country code from the default response for private CIDR addresses.

    Returns:
        The country code string, or None if not configured
    """
    response = get_private_cidr_response()
    if response:
        return response.get("country_code")
    return None
