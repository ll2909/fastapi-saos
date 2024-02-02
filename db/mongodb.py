from pymongo import MongoClient
from jproperties import Properties

config = Properties()
with open("./db/mongodb.properties",  "rb") as f:
    config.load(f)

db_username = config.get("db_username").data
db_pass = config.get("db_pass").data

def get_user_collection():
    uri = config.get("db_uri").data % (db_username, db_pass)
    client = MongoClient(uri)
    db = client.userdb
    collection = db[config.get("db_name").data]
    return collection

def invalid_token(username, token):
    user_collection = get_user_collection()
    user_collection.update_one(filter = {"username" : username}, 
                               update = {"$set" : {"last_used_token" : dict(token)}})