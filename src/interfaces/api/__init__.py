from src.services.hygraph import hygraph
from src.services.lndhub import lndhub
from src.interfaces.api import schemas
from fastapi.responses import JSONResponse
from src.configs import API_HOST, API_PORT, API_DNS
from fastapi import FastAPI, HTTPException, Request
from src.lib import lnurl
from src import database

import uvicorn

# Initialize API.
api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, swagger_ui_oauth2_redirect_url=None)

@api.get("/health/liveness")
async def health_liveness():
    return JSONResponse({"liveness": True})

@api.get("/health/readiness")
async def health_readiness():
    readiness = True
    return JSONResponse({"readiness": readiness}, status_code=(200 if (readiness) else 503))

@api.get("/withdraw/api/v1/lnurl/{user_id}/{voucher}")
def lnurlw_details(user_id: str, voucher: str, request: Request):
    reward = database.Reward.select().where(
        (database.Reward.user == user_id) & 
        (database.Reward.id == voucher))
    if not reward.exists():
        return JSONResponse({
            "status": "ERROR", 
            "reason": "Does not exist"
        }, status_code=204)
    else:
        reward = reward.get()

    return {
        "tag": "withdrawRequest",
        "callback": API_DNS + f"/withdraw/api/v1/lnurl/{user_id}/w",
        "k1": voucher, 
        "minWithdrawable": reward.value * 1000, 
        "maxWithdrawable": reward.value * 1000, 
    }

@api.get("/withdraw/api/v1/lnurl/{user_id}/w")
def lnurlw_execute(user_id: str, k1: str = None, pr: str = None):
    reward = database.Reward.select().where(
        (database.Reward.user == user_id) & 
        (database.Reward.id == k1) & 
        (database.Reward.status == "created"))
    if not reward.exists():
        return JSONResponse({
            "status": "ERROR", 
            "reason": "Does not exist"
        }, status_code=204)
    else:
        reward = reward.get()
    
    try:
        decode_invoice = lndhub.decode_invoice(pr)
    except:
        return JSONResponse({
            "status": "ERROR", 
            "reason": "Invoice is invalid."
        }, status_code=400)
    
    invoice_amount = int(decode_invoice["amount_msat"] / 1000)
    if invoice_amount != reward.value:
        return JSONResponse({
            "status": "ERROR", 
            "reason": "Invoice amount is greater than allowed."
        }, status_code=400)
    
    reward.status = "pending"
    reward.save()
    
    payinvoice = lndhub.payinvoice(pr)
    if not payinvoice.get("payment_preimage"):
        reward.status = "created"
        reward.save()        
        return JSONResponse({
            "status": "ERROR", 
            "reason": "Failed payment."
        }, status_code=500)
    else:
        reward.status = "settled"
        reward.save()             
        return JSONResponse({"status": "OK"})

@api.post("/api/v1/reward/{classroom}")
def reward(classroom: str, data: schemas.QuizSchema, request: Request):
    email = request.headers.get("X-EMAIL")
    if not email:
        raise HTTPException(400, "Invalid email address.")

    user_id = database.User.get_or_create(email=email)[0].id
    if database.Reward.select().where(
        (database.Reward.user == user_id) & 
        (database.Reward.classroom == classroom)).exists():
        raise HTTPException(409, "The prize claim has been created.") 
    
    answers = list(set(data.answers))
    quizzes = hygraph.call(r'''
        {
          quizzes(where: {classroom: "%s"}){
            correctAnswer
          }
        }
    ''' % (classroom))["quizzes"]
    points = len(list(
        filter(lambda data: data["correctAnswer"] \
            in answers, quizzes)))
    
    if not points:
        raise HTTPException(204, "You didn't make any points.")
    
    quizzes_count = len(quizzes)
    quizzes_reward = float(hygraph.call(r'''
        {
            classrooms(where: {classroom: "%s"}) {
                reward
            }
        }
    ''' % (classroom))["classrooms"][0]["reward"])
    porcentagem_prize = points / quizzes_count * 100
    
    value = (quizzes_reward * porcentagem_prize / 100)
    reward = database.Reward.get_or_create(
        user=user_id,
        value=value,
        status="created",
        classroom=classroom
    )[0].id
    return JSONResponse({
        "lnurl": lnurl.lnurl_encode(
            API_DNS + f"/withdraw/api/v1/lnurl/{user_id}/{reward}"
        )
    }, status_code=201)

def start():
    uvicorn.run(api, host=API_HOST, port=API_PORT, loop="asyncio", log_config={
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "foo-logger": {"handlers": ["default"], "level": "DEBUG"},
        },
    })