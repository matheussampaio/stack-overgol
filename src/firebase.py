import configs
import pyrebase

class Firebase:
    database = None
    firebase_app = pyrebase.initialize_app(configs.FIREBASE)

    @staticmethod
    def get_database():
        if Firebase.database is not None:
            return Firebase.database

        Firebase.database = Firebase.firebase_app.database()

        return Firebase.database
