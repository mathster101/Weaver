from flask import Blueprint, request, current_app
from auth import require_api_key
from databaseOpers import DatabaseOperations
from networkOpers import NetworkOperations

database = DatabaseOperations()
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
    clientPublicKey = data['publicKey']
    clientName = data['name']
    
    if database.clientExists(clientPublicKey):
        return {"error": "client already registered"}, 409
 
    allocatedIP = database.fetchUnassignedIP()
    result = network.addClient(clientPublicKey, allocatedIP)
    if "Error" in result:
        return {"error": result}, 400

    database.addNewClient(clientName, clientPublicKey, allocatedIP)
        
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

'''
3. Controller config
sh
ip link add wg0 type wireguard
ip addr add 10.0.0.1/24 dev wg0
wg set wg0 listen-port 51820 private-key ./privatekey
wg set wg0 peer <CLIENT_PUBKEY> allowed-ips 10.0.0.2/32
ip link set wg0 up
4. Client config
sh
ip link add wg0 type wireguard
ip addr add 10.0.0.2/24 dev wg0
wg set wg0 listen-port 51820 private-key ./privatekey
wg set wg0 peer <CONTROLLER_PUBKEY> allowed-ips 10.0.0.0/24 endpoint 192.168.1.1:51820 persistent-keepalive 25
ip link set wg0 up


wg show          # see peer status
ping 10.0.0.1
'''