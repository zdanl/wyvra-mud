from pymongo import MongoClient

import hashlib

class database:

    connection_string = "mongodb://localhost:27017/"
    connection = None
    db = None

    def _hash_password(self, password):
        #password = password.encode()
        hash_obj = hashlib.sha1(password.encode("utf-8"))
        hexa_value = hash_obj.hexdigest()
        return hexa_value

    def check_user(self, user, password):
        success = 0
        r = self.db.users.find_one({"nickname": user})
        if r:
            success += 1
            r = self.db.users.find_one({"password": self._hash_password(password)})
            if r:
                success += 1
        return success

    def register_user(self, user, password):
        hashed = self._hash_password(password)
        self.db.users.insert({"nickname": user, "password": hashed})
        return True

    def delete_user(self, user):
        self.db.users.delete({"nickname": user})

    def __init__(self, database_name="wyvra"):
        self.connection = MongoClient(self.connection_string + database_name)
        self.db = self.connection.wyvra
