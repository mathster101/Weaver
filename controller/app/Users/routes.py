from flask import Blueprint, request, current_app
from auth import require_api_key
from Users.repository import ClientRepository
from networkOpers import NetworkOperations

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
    if not data or 'publicKey' not in data or 'name' not in data:
        return {"error": "missing required fields: publicKey, name"}, 400
    clientPublicKey = data['publicKey']
    clientName = data['name']
    allocatedIP = database.fetchUnassignedIP()
    if allocatedIP is None:
        return {"error": "no available IPs"}, 503
    try:
        database.addNewClient(clientName, clientPublicKey, allocatedIP)
    except ValueError as e:
        return {"error": str(e)}, 409
    result = network.addClient(clientPublicKey, allocatedIP)
    if "Error" in result:
        database.removeClient(clientPublicKey)
        return {"error": result}, 400
    return {
        "controllerPublicKey": fetchControllerPublicKey(),
        "allocatedIP": allocatedIP
    }


@bp_user.route("/peers")
@require_api_key
def peers():
    return {"status": "not implemented"}, 501


def fetchControllerPublicKey():
    publicKey = "invalid"
    with open('publickey', 'r') as f:
        publicKey = f.readline().rstrip('\n')
    return publicKey
