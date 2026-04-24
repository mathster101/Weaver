import os
from flask import Blueprint, request
from functools import wraps

bp = Blueprint("routes", __name__)

def require_api_key(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.headers.get("X-API-Key") != os.environ.get("API_KEY"):
            return {"error": "unauthorized"}, 401
        return f(*args, **kwargs)
    return wrapper

@bp.route("/health")
@require_api_key
def health():
    return {"status": "ok"}
