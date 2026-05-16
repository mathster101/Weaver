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


@bp_user.route('/disconnect', methods=["POST"])
@require_api_key
def disconnectClient():
    data = request.get_json()
    if not data or 'clientPublicKey' not in data:
        return {"error": "missing clientPublicKey"}, 400
    database.removeClient(data['clientPublicKey'])
    return {"status": "ok"}, 200


@bp_user.route("/heartbeat", methods=["POST"])
@require_api_key
def updateHeartbeat():
    data = request.get_json()
    clientPublicKey = data['publicKey']
    database.updateHeartbeat(clientPublicKey)
    return {"status": "ok"}, 200

@bp_user.route("/peers", methods=["GET"])
@require_api_key
def peers():
    clientPublicKey = request.args.get('clientPublicKey')
    if not clientPublicKey:
        return {"error": "missing clientPublicKey"}, 400
    peers = database.fetchPeers(clientPublicKey)
    return {"peers": [{"name": name, "ip": ip} for name, ip in peers]}, 200


def fetchControllerPublicKey():
    publicKey = "invalid"
    with open('publickey', 'r') as f:
        publicKey = f.readline().rstrip('\n')
    return publicKey


#wg show weaver0 dump | awk 'NR>1 {print substr($1,1,16), "RX:", $6, "TX:", $7}'