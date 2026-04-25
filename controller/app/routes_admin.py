from flask import Blueprint
from auth import require_api_key

bp_admin = Blueprint("admin", __name__, url_prefix="/admin")

@bp_admin.route("/users")
@require_api_key
def list_users():
    return {"status": "not implemented"}, 501

@bp_admin.route("/drop-all", methods=["POST"])
@require_api_key
def drop_all():
    return {"status": "not implemented"}, 501

@bp_admin.route("/keys/regen", methods=["POST"])
@require_api_key
def regen_keys():
    return {"status": "not implemented"}, 501
