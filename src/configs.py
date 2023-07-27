from os import getenv

# API configuration.
API_HOST = getenv("API_HOST", "0.0.0.0")
API_PORT = int(getenv("API_PORT", 3214))
API_EXTERNAL = getenv("API_EXTERNAL", f"http://localhost:{API_PORT}")

PRODUCTION = getenv("PRODUCTION", "false")
if (PRODUCTION == "true"):
    PRODUCTION = True
else:
    PRODUCTION = False

class DatabaseConfig:
    
    def __getattr__(self, name: str):
        value = getenv(name)
        if (value):
            if (name == "DB_PORT"):
                value = int(value)
            return value
        elif (name == "DB_TYPE"):
            return "sqlite"
        elif (name == "DB_NAME"):
            return "sqlite"
        elif (name == "DB_HOST"):
            return "127.0.0.1"
        elif (name == "DB_PORT"):
            return 5432
        else:
            return None

# Firebase configuration
FIREBASE_TYPE = getenv("FIREBASE_TYPE", "service_account")
FIREBASE_AUTH_URI = getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
FIREBASE_TOKEN_URI = getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token")
FIREBASE_CLIENT_ID = getenv("FIREBASE_CLIENT_ID")
FIREBASE_PROJECT_ID = getenv("FIREBASE_PROJECT_ID")
FIREBASE_PRIVATE_KEY = getenv("FIREBASE_PRIVATE_KEY")
FIREBASE_CLIENT_EMAIL = getenv("FIREBASE_CLIENT_EMAIL")
FIREBASE_PRIVATE_KEY_ID = getenv("FIREBASE_PRIVATE_KEY_ID")
FIREBASE_UNIVERSE_DOMAIN = getenv("FIREBASE_UNIVERSE_DOMAIN", "googleapis.com")
FIREBASE_CLIENT_X509_CERT_URL = getenv("FIREBASE_CLIENT_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs")
FIREBASE_AUTH_PROVIDER_X509_CERT_URL = getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL")

# MemberStack configuration
MEMBER_STACK_API_KEY = getenv("MEMBER_STACK_API_KEY")

# Hygraph configuration
HYGRAPH_URL = getenv("HYGRAPH_URL")

# Lndhub configuration
LNDHUB_URL = getenv("LNDHUB_URL")
LNDHUB_USERNAME = getenv("LNDHUB_USERNAME")
LNDHUB_PASSWORD = getenv("LNDHUB_PASSWORD")