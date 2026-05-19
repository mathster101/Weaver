import os
import pymongo
from datetime import datetime, UTC

class ClientRepository:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.mongoClient = pymongo.MongoClient(os.environ.get("MONGO_URI"))
            cls._instance.mydb = cls._instance.mongoClient["WeaverDB"]

            cls._instance.clientCollection = cls._instance.mydb["clients"]
            cls._instance.clientCollection.create_index("IP", unique = True)
            cls._instance.clientCollection.create_index("clientPublicKey", unique = True)

            cls._instance.heartbeatCollection = cls._instance.mydb["heartbeats"]
            cls._instance.heartbeatCollection.create_index("clientPublicKey", unique = True)
        return cls._instance
    
    def add_new_client(self, name, clientPublicKey, IP):
        data = {
            "name": name, 
            "clientPublicKey" : clientPublicKey,
            "IP" : IP,
            "connectedAt": datetime.now(UTC)
        }
        try:
            self.clientCollection.insert_one(data)
        except pymongo.errors.DuplicateKeyError as e:
            if "IP" in str(e):
                raise ValueError("IP already allocated")
            raise ValueError("client already registered")
        self.update_heartbeat(clientPublicKey)

    def remove_client(self, clientPublicKey):
        query = {"clientPublicKey" : f"{clientPublicKey}"}
        self.clientCollection.delete_one(query)
        self.heartbeatCollection.delete_one(query)


    def fetch_unassigned_ip(self):
        import ipaddress
        subnet = ipaddress.ip_network("10.0.1.0/24")
        allocatedIPs = {doc["IP"] for doc in self.clientCollection.find({}, {"_id": 0, "IP": 1})}
        for host in subnet.hosts():
            ip = str(host)
            if ip == "10.0.1.1":
                continue
            if ip not in allocatedIPs:
                return ip
        return None
    
    def fetch_peers(self, clientPublicKey):
        # Verify requesting client exists
        requestingClient = self.clientCollection.find_one({"clientPublicKey": clientPublicKey})
        if not requestingClient:
            return None

        allClients = self.clientCollection.find()
        peers = set()
        for client in allClients:
            name = client["name"]
            ip = client["IP"]
            if client["clientPublicKey"] == clientPublicKey:
                name += " (this is you!)"
            peers.add((name, ip))
        return peers


    def update_heartbeat(self, clientPublicKey):
        self.heartbeatCollection.update_one(
            {"clientPublicKey": clientPublicKey},
            {"$set": {"lastHeartbeat": datetime.now(UTC)}},
            upsert=True
        )
