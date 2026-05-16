import requests
from enum import Enum
import subprocess
import argparse
import shlex
import readline
from random import randint
import threading
import time
import signal
import sys


CONTROLLER_IP = "192.168.1.1"

# Global connection state
api_key = None
controllerIP = None
client_name = None
heartbeat_thread = None
heartbeat_running = False

class ClientState(Enum):
    DISCONNECTED = 0
    CONNECTED = 1

def generateKeys():
    subprocess.run(["wg", "genkey"], stdout=open("privatekey", "w"))
    subprocess.run(["wg", "pubkey"], stdin=open("privatekey", "r"), stdout=open("publickey", "w"))

def fetchClientPublicKey():
    with open("publickey", "r") as f:
        return f.readline().strip()



def connectToController(api_key, controllerIP, client_name):
    url = f"http://{controllerIP}:5000/register"
    headers = {"weaver-auth": api_key}
    payload = {
        "publicKey": fetchClientPublicKey(),
        "name": client_name
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"{response.json()['error']}.....exiting")
        return -1
    
    controllerPublicKey = response.json()['controllerPublicKey']
    allocatedIP = response.json()['allocatedIP']

    # Configure WireGuard interface
    subprocess.run(["ip", "link", "delete", "weaverClient0"], capture_output=True)
    subprocess.run(["ip", "link", "add", "weaverClient0", "type", "wireguard"])
    subprocess.run(["ip", "addr", "add", f"{allocatedIP}/24", "dev", "weaverClient0"])
    subprocess.run(["wg", "set", "weaverClient0", "listen-port", "51820", "private-key", "./privatekey"])
    subprocess.run(["wg", "set", "weaverClient0", "peer", controllerPublicKey, "allowed-ips", "10.0.0.0/24", "endpoint", f"{controllerIP}:51820", "persistent-keepalive", "15"])
    subprocess.run(["ip", "link", "set", "weaverClient0", "up"])
    
    return 0

def sendHeartbeat():
    global api_key, controllerIP, client_name, heartbeat_running
    url = f"http://{controllerIP}:5000/heartbeat"
    headers = {"weaver-auth": api_key}
    payload = {
        "publicKey": fetchClientPublicKey()
    }

    while heartbeat_running:
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                pass
        except Exception as e:
            print(f"Heartbeat failed: {e}")
        time.sleep(2)

def listPeers():
    global api_key, controllerIP
    url = f"http://{controllerIP}:5000/peers?clientPublicKey={fetchClientPublicKey()}"
    headers = {"weaver-auth": api_key}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            peers = response.json()['peers']
            if not peers:
                print("No peers connected")
            else:
                print("Connected peers:")
                for peer in peers:
                    print(f"  - {peer['name']} ({peer['ip']})")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Failed to fetch peers: {e}")

def disconnectFromController():
    global api_key, controllerIP
    url = f"http://{controllerIP}:5000/disconnect"
    headers = {"weaver-auth": api_key}
    payload = {
        "clientPublicKey": fetchClientPublicKey()
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Disconnected from controller")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Failed to disconnect: {e}")

def signal_handler(sig, frame):
    global state, heartbeat_running
    if state == ClientState.CONNECTED:
        print("\nDisconnecting...")
        disconnectFromController()
        heartbeat_running = False
    sys.exit(0)
    

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    for i in range(randint(1, 100)):
        generateKeys()
    print("keys shuffled!")
    parser = argparse.ArgumentParser(prog='', add_help=False)
    subparsers = parser.add_subparsers(dest='command')

    connect_parser = subparsers.add_parser('connect')
    connect_parser.add_argument('--api_key', required=True)
    connect_parser.add_argument('--controller_ip', default=CONTROLLER_IP)
    connect_parser.add_argument('--client_name', required=True)

    subparsers.add_parser('show_pub_key')

    subparsers.add_parser('regen_keys')

    subparsers.add_parser('disconnect')

    subparsers.add_parser('list_peers')

    state = ClientState.DISCONNECTED
    try:
        while True:
            cmd_input = input('>').strip()
            parts = shlex.split(cmd_input) if cmd_input else []

            if not parts:
                continue

            # Validate command for current state before argparse
            if state == ClientState.DISCONNECTED:
                valid_commands = ['connect', 'regen_keys', 'show_pub_key']
            elif state == ClientState.CONNECTED:
                valid_commands = ['disconnect', 'list_peers']
            else:
                valid_commands = []

            if parts[0] not in valid_commands:
                print(f"Unknown command: {parts[0]} (available: {', '.join(valid_commands)})")
                continue

            try:
                args = parser.parse_args(parts)
            except (SystemExit, ValueError):
                continue

            if state == ClientState.DISCONNECTED:
                if args.command == 'connect':
                    global api_key, controllerIP, client_name, heartbeat_thread, heartbeat_running
                    api_key = args.api_key
                    controllerIP = args.controller_ip
                    client_name = args.client_name
                    result = connectToController(api_key, controllerIP, client_name)
                    if result == 0:
                        state = ClientState.CONNECTED
                        print("Connected successfully")
                        # Start heartbeat thread
                        heartbeat_running = True
                        heartbeat_thread = threading.Thread(target=sendHeartbeat, daemon=True)
                        heartbeat_thread.start()
                elif args.command == 'regen_keys':
                    generateKeys()
                    print("Keys regenerated")
                elif args.command == 'show_pub_key':
                    print(fetchClientPublicKey())

            elif state == ClientState.CONNECTED:
                if args.command == 'disconnect':
                    disconnectFromController()
                    heartbeat_running = False
                    state = ClientState.DISCONNECTED
                    print("Disconnected")
                elif args.command == 'list_peers':
                    listPeers()
    except KeyboardInterrupt:
        if state == ClientState.CONNECTED:
            print("\nDisconnecting...")
            disconnectFromController()
            heartbeat_running = False

if __name__ == '__main__':
    main()
