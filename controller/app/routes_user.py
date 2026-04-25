from flask import Blueprint
from auth import require_api_key

bp_user = Blueprint("user", __name__)

@bp_user.route("/health")
@require_api_key
def health():
    return {"status": "ok"}

@bp_user.route("/connect", methods=["POST"])
@require_api_key
def connect():
    return {"status": "not implemented"}, 501

@bp_user.route("/disconnect", methods=["POST"])
@require_api_key
def disconnect():
    return {"status": "not implemented"}, 501

@bp_user.route("/peers")
@require_api_key
def peers():
    return {"status": "not implemented"}, 501


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