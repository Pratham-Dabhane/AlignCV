"""
API Helper Functions
Safe JSON parsing and error handling for API responses
"""

import json
import requests
from typing import Dict, Any, Optional

def safe_json_parse(response: requests.Response) -> Optional[Dict[str, Any]]:
    """
    Safely parse JSON response with error handling
    
    Args:
        response: requests.Response object
        
    Returns:
        Parsed JSON data or None if parsing fails
    """
    try:
        if response.text.strip():
            return response.json()
        else:
            return None
    except json.JSONDecodeError:
        return None

def get_error_message(response: requests.Response, default_msg: str = "Request failed") -> str:
    """
    Extract error message from response
    
    Args:
        response: requests.Response object
        default_msg: Default message if no error found
        
    Returns:
        Error message string
    """
    try:
        if response.text.strip():
            data = response.json()
            return data.get("detail", default_msg)
        else:
            return f"{default_msg} (Status: {response.status_code})"
    except json.JSONDecodeError:
        return f"{default_msg} (Status: {response.status_code})"

def handle_api_response(response: requests.Response, success_callback=None, error_callback=None):
    """
    Handle API response with proper error handling
    
    Args:
        response: requests.Response object
        success_callback: Function to call on success
        error_callback: Function to call on error
    """
    if response.status_code in [200, 201]:
        data = safe_json_parse(response)
        if data is not None:
            if success_callback:
                success_callback(data)
        else:
            if error_callback:
                error_callback("Invalid response from server")
    else:
        error_msg = get_error_message(response)
        if error_callback:
            error_callback(error_msg)
