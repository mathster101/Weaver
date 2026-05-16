import pyroute2
import subprocess

class NetworkOperations:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.iproute = pyroute2.IPRoute()
            existing = cls._instance.iproute.link_lookup(ifname="weaver0")
            if existing:
                cls._instance.iproute.link("del", index=existing[0])
            cls._instance.iproute.link("add", ifname="weaver0", kind="wireguard")
            index = cls._instance.iproute.link_lookup(ifname="weaver0")[0]
            cls._instance.iproute.addr("add", index=index, address="10.0.0.1", prefixlen=24)
            cls._instance.iproute.link("set", index=index, state="up")
            subprocess.run(["wg", "set", "weaver0", "listen-port", "51820", "private-key", "./privatekey"])
        return cls._instance

    def addClient(self, clientPublicKey, clientIP):
        checkExistingResult = subprocess.run(["wg", "show", "weaver0", "dump"], capture_output=True, text=True)
        if clientPublicKey in checkExistingResult.stdout:
            return "Client already connected"
        addClientResult = subprocess.run(["wg", "set", "weaver0", "peer", str(clientPublicKey), "allowed-ips", f"{clientIP}/32"], capture_output=True, text=True)
        if addClientResult.returncode != 0:
            return f"Error: {addClientResult.stderr}"
        return "Client added successfully"