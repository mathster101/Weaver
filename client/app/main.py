import argparse

def connect(server):
    print(f"Connecting to Weaver controller at {server}...")

def disconnect(server):
    print(f"Disconnecting from Weaver controller at {server}...")

def status():
    print("Weaver status...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="weaver")
    subparsers = parser.add_subparsers(dest="command")

    connect_parser = subparsers.add_parser("connect")
    connect_parser.add_argument("--server", required=True, help="Controller IP or hostname")

    disconnect_parser = subparsers.add_parser("disconnect")
    disconnect_parser.add_argument("--server", required=True, help="Controller IP or hostname")

    subparsers.add_parser("status")

    args = parser.parse_args()

    if args.command == "connect":
        connect(args.server)
    elif args.command == "disconnect":
        disconnect(args.server)
    elif args.command == "status":
        status()
    else:
        parser.print_help()
