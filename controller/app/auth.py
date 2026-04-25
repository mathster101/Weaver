import os
from flask import request
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.headers.get("weaver-auth") != os.environ.get("API_KEY"):
            return {"error": "unauthorized"}, 401
        return f(*args, **kwargs)
    return wrapper
