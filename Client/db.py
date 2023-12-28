from pymongo import MongoClient
import hashlib
import uuid

# Includes database operations
class DB:

    # db initializations
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['p2p-chat']

    # checks if an account with the username exists
    def is_account_exist(self, username):
        if self.db.accounts.find({'username': username}).count() > 0:
            return True
        else:
            return False

    # registers a user
    def register(self, username, password):
        hashedPassword = hashlib.md5(password.encode()).hexdigest()
        account = {
            "username": username,
            "password": hashedPassword
        }
        self.db.accounts.insert(account)

    def create_room(self, name):
        id = uuid.uuid4()
        room = {
            "id": id,
            "name": id
        }
        self.db.rooms.insert(room)

    # 0-> normal, 1-> joined, 2-> left
    def add_message_to_room(self, room_id, message, sender_username, message_type):
        message = {
            "room_id": room_id,
            "message": message,
            "sender_username": sender_username,
            "message_type": message_type
        }
        self.db.room_messages.insert(message)

    # retrieves the password for a given username
    def get_password(self, username):
        return self.db.accounts.find_one({"username": username})["password"]

    # checks if an account with the username online
    def is_account_online(self, username):
        if self.db.online_peers.find({"username": username}).count() > 0:
            return True
        else:
            return False

    # logs in the user
    def user_login(self, username, ip, port):
        online_peer = {
            "username": username,
            "ip": ip,
            "port": port
        }
        self.db.online_peers.insert(online_peer)

    # logs out the user 
    def user_logout(self, username):
        self.db.online_peers.remove({"username": username})

    # retrieves the ip address and the port number of the username
    def get_peer_ip_port(self, username):
        res = self.db.online_peers.find_one({"username": username})
        return (res["ip"], res["port"])

    def get_online_peers(self, excluded_username):
        result = list(self.db.online_peers.aggregate(self.generate_pipeline(excluded_username)))
        if result:
            comma_separated_usernames = result[0]["usernames"]
            return comma_separated_usernames

        return ""

    def generate_pipeline(self, excluded_username):
        match_stage = {
            "$match": {
                "username": {"$ne": excluded_username}  # Exclude the specified username
            }
        }

        group_stage = {
            "$group": {
                "_id": None,
                "usernames": {"$push": "$username"}  # Push all usernames into an array
            }
        }

        project_stage = {
            "$project": {
                "_id": 0,
                "usernames": {
                    "$reduce": {
                        "input": "$usernames",
                        "initialValue": "",
                        "in": {
                            "$cond": [
                                {"$eq": ["$$value", ""]},
                                "$$this",
                                {"$concat": ["$$value", ",", "$$this"]}
                            ]
                        }
                    }
                }
            }
        }

        return [match_stage, group_stage, project_stage]
