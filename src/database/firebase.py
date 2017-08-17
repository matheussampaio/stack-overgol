import logging
import pyrebase

from utils import configs
from models.user import User

logger = logging.getLogger(__name__)

settings = {
    "apiKey": configs.get("FIREBASE.API_KEY"),
    "authDomain": configs.get("FIREBASE.AUTH_DOMAIN"),
    "databaseURL": configs.get("FIREBASE.DATA_BASE_URL"),
    "storageBucket": configs.get("FIREBASE.STORAGE_BUCKET"),
    "serviceAccount": configs.get("FIREBASE.SERVICE_ACCOUNT")
}

database = pyrebase.initialize_app(settings).database()
