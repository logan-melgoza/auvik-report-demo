import os
import json
import time
from pathlib import Path
from typing import Dict

DATA_DIR = Path('data')
CACHE_DIR = DATA_DIR / 'cache'
CACHE_TTL = 3600

def set_file_path(tenant: str) -> str:
    """
    Uses the tenant name to create a path to JSON file

    Args:
        Tenant (str): The name of the tenant
    
    Returns:
        str: The file path
    """
    return f'{CACHE_DIR}/{tenant}_cache.json'

def get_cache(tenant: str) -> Dict:
    """
    Get cached API responses for report elements if they exist within a certain time frame (CACHE_TTL)
    
    Args:
        tenant (str): The name of the tenant

    Return:
        Dict: Cached data
    """
    file = set_file_path(tenant)
    if os.path.exists(file):
        with open(file, 'r') as f:
            cache = json.load(f)
        if time.time() - cache.get("timestamp", 0) < CACHE_TTL:
            return cache.get("data")
    return None

def set_cache(data: Dict, tenant: str) -> None:
    """
    Caches a fresh API response

    Args:
        data (Dict): All report elements received from API calls
        tenant (str): The tenant name
    
    Returns:
        None
    """
    file = set_file_path(tenant)

    DATA_DIR.mkdir(exist_ok=True)

    CACHE_DIR.mkdir(exist_ok=True)

    with open(file, 'w') as f:
        json.dump({"timestamp": time.time(), "data": data}, f)
