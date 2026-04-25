import os
import pymongo

class DatabaseOperations:
    def __init__(self):
        self.mongoClient = pymongo.MongoClient(os.environ.get("MONGO_URI"))
        self.mydb = self.mongoClient["WeaverDB"]
        self.clients = self.mydb["clients"]
    
    def clientExists(self, clientPublicKey):
        return self.clients.count_documents({"clientPublicKey": clientPublicKey}) > 0

    def addNewClient(self, name, clientPublicKey, IP):
        data = {
            "name": name, 
            "clientPublicKey" : clientPublicKey,
            "IP" : IP
        }
        self.clients.insert_one(data)

    def fetchUnassignedIP(self):
        import ipaddress
        subnet = ipaddress.ip_network("10.0.0.0/24")
        allocatedIPs = {doc["IP"] for doc in self.clients.find({}, {"_id": 0, "IP": 1})}
        for host in subnet.hosts():
            ip = str(host)
            if ip == "10.0.0.1":
                continue
            if ip not in allocatedIPs:
                return ip
        return None