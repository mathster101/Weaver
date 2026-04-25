import os
from flask import Flask
from pymongo import MongoClient
from routes_user import bp_user
from routes_admin import bp_admin

app = Flask(__name__)
app.register_blueprint(bp_user)
app.register_blueprint(bp_admin)

# mongo = MongoClient(os.environ.get("MONGO_URI"))
# db = mongo["weaver"]
# app.config["client_repo"] = ClientRepository(db)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
