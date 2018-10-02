import logging
import pyrebase

from utils.config import Config
from models.user import User

logger = logging.getLogger(__name__)

settings = {
    "apiKey": Config.firebase_api_key(),
    "authDomain": Config.firebase_auth_domain(),
    "databaseURL": Config.firebase_data_base_url(),
    "storageBucket": Config.firebase_storage_bucket(),
    "serviceAccount": Config.firebase_service_account()
}

database = pyrebase.initialize_app(settings).database()
