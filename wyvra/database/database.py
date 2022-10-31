from pymongo import MongoClient

class database:

    connection_string = "mongodb://localhost:27017/"
    connection = None

    def check_user(user, password):
        r = self.connection.users.findOne({"nickname": user, "password": password})
        if r:
            return True

    def __init__(self, database_name="wyvra"):
        self.connection = MongoClient(self.connection_string + database_name)
