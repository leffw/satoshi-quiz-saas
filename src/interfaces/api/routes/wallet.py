from src.lib.lndhub import LndHub
from fastapi import APIRouter, Request
from src import database

import logging

router = APIRouter()

@router.get("/api/v1/balance")
def get_balance(request: Request = Request):
    """
    Retrieve the available balance in Bitcoin (BTC) for the user associated with the Request.

    Args:
        request (Request, optional): The FastAPI request object. If not provided, the default
        object from the function will be used.

    Returns:
        dict: A dictionary containing the "balance" key with the available balance value in BTC.
    """
    lndhub = database.Lndhub.select().where(
        (database.Lndhub.user == request.data["id"])).get()
    lndhub = LndHub(
        url=lndhub.url,
        username=lndhub.username,
        password=lndhub.password
    )
    try:
        balance = lndhub.get_balance()["BTC"]["AvailableBalance"]
    except Exception as error:
        logging.error(str(error), exc_info=True)
        balance = 0

    return { "balance": balance }

@router.post("/api/v1/invoice")
def create_invoice(request: Request = Request):
    """
    Create a new payment invoice using the LndHub service associated with the user.

    Args:
        request (Request, optional): The FastAPI request object. If not provided, the default
        object from the function will be used.

    Returns:
        dict: A dictionary containing the "invoice" key with the newly created invoice value.
    """
    lndhub = database.Lndhub.select().where(
        (database.Lndhub.user == request.data["id"])).get()
    lndhub = LndHub(
        url=lndhub.url,
        username=lndhub.username,
        password=lndhub.password
    )
    invoice = lndhub.addinvoice(0)
    return { "invoice": invoice["payment_request"] }
