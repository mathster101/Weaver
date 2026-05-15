import requests
from enum import Enum
import subprocess
import argparse
import shlex

CONTROLLER_IP = "192.168.1.1"
NAME = "MATHEWCLIENT1"


class ClientState(Enum):
    DISCONNECTED = 0
    CONNECTED = 1

def generateKeys():
    subprocess.run(["wg", "genkey"], stdout=open("privatekey", "w"))
    subprocess.run(["wg", "pubkey"], stdin=open("privatekey", "r"), stdout=open("publickey", "w"))

def fetchClientPublicKey():
    with open("publickey", "r") as f:
        return f.readline().strip()



def connectToController(api_key, controller_ip):
    url = f"http://{controller_ip}:5000/register"
    headers = {"weaver-auth": api_key}
    payload = {
        "publicKey": fetchClientPublicKey(),
        "name": NAME
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"{response.json()['error']}.....exiting")
        return -1
    
    controllerPublicKey = response.json()['controllerPublicKey']
    allocatedIP = response.json()['allocatedIP']

    # Configure WireGuard interface
    subprocess.run(["ip", "link", "add", "wg0", "type", "wireguard"])
    subprocess.run(["ip", "addr", "add", f"{allocatedIP}/24", "dev", "wg0"])
    subprocess.run(["wg", "set", "wg0", "listen-port", "51820", "private-key", "./privatekey"])
    subprocess.run(["wg", "set", "wg0", "peer", controllerPublicKey, "allowed-ips", "10.0.0.0/24", "endpoint", f"{controller_ip}:51820", "persistent-keepalive", "25"])
    subprocess.run(["ip", "link", "set", "wg0", "up"])
    
    return 0
    
    

def main():
    parser = argparse.ArgumentParser(prog='', add_help=False)
    subparsers = parser.add_subparsers(dest='command')

    connect_parser = subparsers.add_parser('connect')
    connect_parser.add_argument('--api_key', required=True)
    connect_parser.add_argument('--controller_ip', default=CONTROLLER_IP)
    
    subparsers.add_parser('regen_keys')

    subparsers.add_parser('disconnect')

    subparsers.add_parser('list_peers')

    state = ClientState.DISCONNECTED
    while True:
        cmd_input = input('>').strip()
        parts = shlex.split(cmd_input) if cmd_input else []
        
        if not parts:
            continue

        # Validate command for current state before argparse
        if state == ClientState.DISCONNECTED:
            valid_commands = ['connect', 'regen_keys']
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
                result = connectToController(args.api_key, args.controller_ip)
                if result == 0:
                    state = ClientState.CONNECTED
                    print("Connected successfully")
            elif args.command == 'regen_keys':
                generateKeys()
                print("Keys regenerated")

        elif state == ClientState.CONNECTED:
            if args.command == 'disconnect':
                state = ClientState.DISCONNECTED
                print("Disconnected")
            elif args.command == 'list_peers':
                print("list_peers not implemented yet")

if __name__ == '__main__':
    main()
