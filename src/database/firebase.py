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
    "serviceAccount": {
        "type": "service_account",
        "project_id": Config.firebase_project_id(),
        "private_key_id": Config.firebase_private_key_id(),
        "private_key": Config.firebase_private_key(),
        "client_email": Config.firebase_client_email(),
        "client_id": Config.firebase_client_id(),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-kur77%40stack-overgol-bot.iam.gserviceaccount.com"
    }
}

database = pyrebase.initialize_app(settings).database()
