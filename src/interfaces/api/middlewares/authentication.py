from src.services.firebase import verify_id_token
from fastapi import Request, HTTPException
from src import database

import logging

def isAuthentication(request: Request):
    if "/api/v1/lnurl/withdraw/" in request.url.path:
        return request
    
    if "/api/v1/reward/" in request.url.path:
        return request
    
    if "/api/v1/q/" in request.url.path:
        return request

    if request.url.path in [
        "/health/liveness",
        "/health/readiness",
    ]:
        return request
    
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(401)
    else:
        authorization = authorization.split(" ")[-1]
    
        try:
            user = verify_id_token(authorization)
            email = user["email"]
            user_id = user["uid"] 
        except Exception as error:
            logging.error(str(error), exc_info=True)
            raise HTTPException(401)
        
        if not database.User.select(database.User.id).where(
            (database.User.id == user_id) &
            (database.User.email == email)).exists():
            database.User.create(id=user_id, email=email)
        
        request.data = { "id": user_id }
        return request