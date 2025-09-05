import hashlib
import json 
from typing import Any, Union, List, Dict

def generate_cache_key(data: Any, prefix: str ="ml_pred") -> str:
    """Generate a consistant cache key from input data"""
    if isinstance(data, dict):
        normalized = json.dumps(data, sort_keys = True, default = str)
    elif isinstance(data, List):
        normalized = json.dumps(data, default = str) 
    else:
        normalized = str(data)

    hash_object = hashlib.sha256(normalized.encode()) 
    hash_hex = hash_object.hexdigest()[:16] 
    return f"{prefix}:{hash_hex}" 
