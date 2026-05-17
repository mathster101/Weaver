from flask import Blueprint, request, current_app
from auth import require_api_key
from Users.repository import ClientRepository
from .networkOpers import NetworkOperations

database = ClientRepository()
network = NetworkOperations()

bp_user = Blueprint("user", __name__)

@bp_user.route("/health")
@require_api_key
def health():
    return {"status": "ok"}

@bp_user.route("/register", methods=["POST"])
@require_api_key
def registerClient():
    data = request.get_json()
    if not data or "publicKey" not in data or "name" not in data:
        return {"error": "missing required fields: publicKey, name"}, 400
    clientPublicKey = data["publicKey"]
    clientName = data["name"]

    # Check if client already exists
    existingClient = database.clientCollection.find_one_and_update(
        {"clientPublicKey": clientPublicKey},
        {"$set": {"name": clientName}}  # Update name in case it changed
    )
    if existingClient:
        allocatedIP = existingClient["IP"]
        # Re-add to WireGuard in case controller restarted
        result = network.add_client(clientPublicKey, allocatedIP)
        if "Error" in result:
            return {"error": result}, 400
        database.update_heartbeat(clientPublicKey)
        return {
            "controllerPublicKey": fetchControllerPublicKey(),
            "allocatedIP": allocatedIP
        }

    # new client registration
    allocatedIP = database.fetch_unassigned_ip()
    if allocatedIP is None:
        return {"error": "no available IPs"}, 503
    try:
        database.add_new_client(clientName, clientPublicKey, allocatedIP)
    except ValueError as e:
        return {"error": str(e)}, 409
    result = network.add_client(clientPublicKey, allocatedIP)
    if "Error" in result:
        database.remove_client(clientPublicKey)
        return {"error": result}, 400
    return {
        "controllerPublicKey": fetchControllerPublicKey(),
        "allocatedIP": allocatedIP
    }


@bp_user.route("/disconnect", methods=["POST"])
@require_api_key
def disconnectClient():
    data = request.get_json()
    if not data or "clientPublicKey" not in data:
        return {"error": "missing clientPublicKey"}, 400
    database.remove_client(data["clientPublicKey"])
    return {"status": "ok"}, 200


@bp_user.route("/heartbeat", methods=["POST"])
@require_api_key
def updateHeartbeat():
    data = request.get_json()
    clientPublicKey = data["publicKey"]
    database.update_heartbeat(clientPublicKey)
    return {"status": "ok"}, 200

@bp_user.route("/peers", methods=["GET"])
@require_api_key
def peers():
    clientPublicKey = request.args.get("clientPublicKey")
    if not clientPublicKey:
        return {"error": "missing clientPublicKey"}, 400
    peers = database.fetch_peers(clientPublicKey)
    if peers is None:
        return {"error": "client not found"}, 404
    return {"peers": [{"name": name, "ip": ip} for name, ip in peers]}, 200


def fetchControllerPublicKey():
    publicKey = "invalid"
    with open("publickey", "r") as f:
        publicKey = f.readline().rstrip("\n")
    return publicKey


#wg show weaver0 dump | awk 'NR>1 {print substr($1,1,16), "RX:", $6, "TX:", $7}'