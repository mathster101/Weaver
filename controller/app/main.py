import os
from flask import Flask
from Users.routes import bp_user
from Users.networkOpers import NetworkOperations
from multiprocessing import Process
from workers.monitor import HeartbeatMonitor

def setup():
    NetworkOperations()
    app = Flask(__name__)
    app.register_blueprint(bp_user)
    return app

if __name__ == "__main__":
    # Start monitor process
    monitor_process = Process(target=HeartbeatMonitor().run)
    monitor_process.daemon = True
    monitor_process.start()
    
    app = setup()
    app.run(host="0.0.0.0", port=5000, debug=True)
