import time
import pymongo
import os
import subprocess


class HeartbeatMonitor:
    def __init__(self):
        self.mongoClient = None
        self.heartbeatCollection = None
        self.clientCollection = None
    
    def _init_db(self):
        if self.mongoClient is None:
            self.mongoClient = pymongo.MongoClient(os.environ.get("MONGO_URI"))
            mydb = self.mongoClient["WeaverDB"]
            self.heartbeatCollection = mydb["heartbeats"]
            self.clientCollection = mydb["clients"]
    
    def run(self, interval=1):
        """Run the monitor loop with specified interval in seconds."""
        self._init_db()
        print(f"Starting heartbeat monitor with {interval}s interval...")
        while True:
            self.purgeInactiveClients()
            time.sleep(interval)

    def purgeInactiveClients(self):
        now = time.time()
        allHeartbeats = self.heartbeatCollection.find()
        for clientHeartbeat in allHeartbeats:
            last_heartbeat = clientHeartbeat['lastHeartbeat'].timestamp()
            if now - last_heartbeat > 10:
                query = {"clientPublicKey" : clientHeartbeat["clientPublicKey"]}
                self.heartbeatCollection.delete_one(query)
                self.clientCollection.delete_one(query)
                try:
                    subprocess.run(f"wg set weaver0 peer {clientHeartbeat['clientPublicKey']} remove", shell=True)
                except Exception as e:
                    print(f"Failed to remove WireGuard peer: {e}")
                print(f"timeout - {clientHeartbeat['clientPublicKey']}")


if __name__ == "__main__":
    monitor = HeartbeatMonitor()
    monitor.run()
