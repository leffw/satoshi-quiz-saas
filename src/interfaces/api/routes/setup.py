from src.interfaces.api.schemas import LndhubSchema, MemberStackSchema
from fastapi.responses import JSONResponse
from src.lib.lndhub import LndHub
from fastapi import APIRouter, Request, HTTPException
from src import database

import logging

router = APIRouter()

@router.post("/api/v1/setup/lndhub")
def lndhub(data: LndhubSchema, request: Request):
    """
    Create a new Lndhub entry for a user.

    Args:
        data (LndhubSchema): The data containing the Lndhub information.
        request (Request): The FastAPI request object.

    Returns:
        JSONResponse: A JSON response indicating the success of the operation or an error.

    Raises:
        HTTPException: If an Lndhub entry already exists for the user, it raises a 204 status code.
    """
    user_id = request.data["id"]
    try:
        lndhub = LndHub(url=data.url, username=data.username, password=data.password)
        lndhub.get_balance()["BTC"]["AvailableBalance"]
    except Exception as error:
        logging.error(str(error), exc_info=True)
        raise HTTPException(400, "This Lndhub is invalid.")

    lndhub = database.Lndhub.select().where(
        (database.Lndhub.user == user_id))
    if not lndhub.exists():
        database.Lndhub.create(
            user=user_id,
            url=data.url,
            username=data.username,
            password=data.password
        )
    else:
        lndhub = lndhub.get()
        lndhub.url = data.url
        lndhub.username = data.username
        lndhub.password = data.password
        lndhub.save()
    
    return JSONResponse({ "message": "Lndhub has been successfully created." })

@router.post("/api/v1/setup/memberstack")
def memberstack(data: MemberStackSchema, request: Request):
    """
    Create a new MemberStack entry for a user.

    Args:
        data (MemberStackSchema): The data containing the MemberStack information.
        request (Request): The FastAPI request object.

    Returns:
        JSONResponse: A JSON response indicating the success of the operation or an error.

    Raises:
        HTTPException: If a MemberStack entry already exists for the user, 
        it raises a 204 status code.
    """
    user_id = request.data["id"]
    if database.MemberStack.select(database.MemberStack.user).where(
        (database.MemberStack.user == user_id)).exists():
        raise HTTPException(204)

    database.MemberStack.create(user=user_id, key=data.key)
    return JSONResponse(
        {"message": "MemberStack has been successfully created." }, status_code=201)
