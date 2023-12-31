from firebase_admin import credentials, auth, initialize_app
from src.configs import FIREBASE_AUTH_PROVIDER_X509_CERT_URL, FIREBASE_AUTH_URI, FIREBASE_CLIENT_EMAIL, FIREBASE_CLIENT_ID, FIREBASE_CLIENT_X509_CERT_URL, FIREBASE_PRIVATE_KEY, FIREBASE_PRIVATE_KEY_ID, FIREBASE_PROJECT_ID, FIREBASE_TOKEN_URI, FIREBASE_TYPE

cred = credentials.Certificate({
    "type": FIREBASE_TYPE,
    "project_id": FIREBASE_PROJECT_ID,
    "private_key_id": FIREBASE_PRIVATE_KEY_ID,
    "private_key": FIREBASE_PRIVATE_KEY,
    "client_email": FIREBASE_CLIENT_EMAIL,
    "client_id": FIREBASE_CLIENT_ID,
    "auth_uri": FIREBASE_AUTH_URI,
    "token_uri": FIREBASE_TOKEN_URI,
    "auth_provider_x509_cert_url": FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
    "client_x509_cert_url": FIREBASE_CLIENT_X509_CERT_URL
})

# Initialize Firebase Admin SDK 
# with the credentials
initialize_app(cred)

def verify_id_token(token: str) -> dict:
    return auth.verify_id_token(
        token, 
        check_revoked=True
    )
