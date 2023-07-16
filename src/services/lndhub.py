from src.lib.lndhub import LndHub
from src.configs import LNDHUB_URL, LNDHUB_USERNAME, LNDHUB_PASSWORD

lndhub = LndHub(
    url=LNDHUB_URL,
    username=LNDHUB_USERNAME,
    password=LNDHUB_PASSWORD
)