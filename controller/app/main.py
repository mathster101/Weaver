import os
from flask import Flask
from routes_user import bp_user
from routes_admin import bp_admin
from networkOpers import NetworkOperations

def setup():
    NetworkOperations()
    app = Flask(__name__)
    app.register_blueprint(bp_user)
    app.register_blueprint(bp_admin)
    return app

if __name__ == "__main__":
    app = setup()
    app.run(host="0.0.0.0", port=5000, debug=True)
