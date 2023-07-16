from .bech32 import bech32_decode, bech32_encode, convertbits

def lnurl_decode(lnurl: str) -> str:
    """
    Decode an lnurl to retrieve the underlying data.

    Parameters:
        lnurl (str): The lnurl to be decoded.
    """
    _, data = bech32_decode(lnurl.upper().replace("LIGHTNING:", ""))
    return bytes(convertbits(data, 5, 8, False)).decode("utf-8")

def lnurl_encode(url: str) -> str:
    """
    Encode a URL to lnurl format.

    Parameters:
        url (str): The URL to be encoded.
    """
    return bech32_encode(
        "lnurl", convertbits(url.encode("utf-8"), 8, 5, True)).upper()
