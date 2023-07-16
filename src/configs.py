from os import getenv

# API configuration.
API_HOST = getenv("API_HOST", "0.0.0.0")
API_PORT = int(getenv("API_PORT", 3214))

API_DNS = getenv("API_DNS", f"http://localhost:{API_PORT}")

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

# Hygraph configuration
HYGRAPH_URL = getenv("HYGRAPH_URL")

# Lndhub configuration
LNDHUB_URL = getenv("LNDHUB_URL")
LNDHUB_USERNAME = getenv("LNDHUB_USERNAME")
LNDHUB_PASSWORD = getenv("LNDHUB_PASSWORD")