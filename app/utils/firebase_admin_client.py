import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

def init_firebase():
    if not firebase_admin._apps:
        cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
        if not cred_path:
            raise RuntimeError("FIREBASE_CREDENTIALS_PATH not set")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

auth = firebase_auth
