from fastapi.middleware.cors import CORSMiddleware
from src.services.memberstack import memberstack
from src.services.hygraph import hygraph
from src.services.lndhub import lndhub
from src.interfaces.api import schemas
from fastapi.responses import JSONResponse
from src.configs import API_HOST, API_PORT, API_DNS
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from src.lib import lnurl
from base64 import b64decode
from uuid import uuid4
from src import database

import logging
import uvicorn

# Initialize API.
api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, swagger_ui_oauth2_redirect_url=None)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        }, status_code=400)
    else:
        reward = reward.get()

    return {
        "tag": "withdrawRequest",
        "callback": API_DNS + f"/withdraw/api/v1/lnurlw/{user_id}",
        "k1": voucher, 
        "minWithdrawable": reward.value * 1000, 
        "maxWithdrawable": reward.value * 1000, 
    }

@api.get("/withdraw/api/v1/lnurlw/{user_id}")
def lnurlw_execute(user_id: str, k1: str = None, pr: str = None):
    reward = database.Reward.select().where(
        (database.Reward.user == user_id) & 
        (database.Reward.id == k1) & 
        (database.Reward.status == "created"))
    if not reward.exists():
        logging.error("Reward does not exist")
        return JSONResponse({
            "status": "ERROR", 
            "reason": "Does not exist"
        }, status_code=400)
    else:
        reward = reward.get()
    
    try:
        decode_invoice = lndhub.decode_invoice(pr)
    except:
        return JSONResponse({
            "status": "ERROR", 
            "reason": "Invoice is invalid."
        }, status_code=400)
    
    invoice_amount = decode_invoice["num_satoshis"]
    if invoice_amount != reward.value:
        return JSONResponse({
            "status": "ERROR", 
            "reason": "Invoice amount is greater than allowed."
        }, status_code=400)
    
    reward.status = "pending"
    reward.save()
    
    try:    
        payinvoice = lndhub.payinvoice(pr)
    except:
        payinvoice = {}
    
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
def reward(classroom: str, data: schemas.QuizSchema, request: Request, background_tasks: BackgroundTasks):
    user_id = request.headers.get("X-USER-ID")
    if not user_id or user_id == "null":
        raise HTTPException(401, "Invalid User-Id address.")

    def create_reward(user_id: str, reward_id: str):
        try:
            answers = b64decode(data.answers).decode("utf-8")
        except:
            answers = b64decode(data.answers).decode("latin-1")
        
        answers = list(set(answers.split("&")))
        quizzes_and_classroom = hygraph.call(r'''
            {
                quizzes(where: {classroom: "%s"}) {
                    correctAnswer
                }
                
                classrooms(where: {classroom: "%s"}) {
                    reward
                }
            }
        ''' % (classroom, classroom))
        points = len(list(
            filter(lambda data: data["correctAnswer"] \
                in answers, quizzes_and_classroom["quizzes"])))
        
        if not points:
            return logging.error(f"{user_id} has no required points")
        
        quizzes_count = len(quizzes_and_classroom["quizzes"])
        quizzes_reward = float(quizzes_and_classroom["classrooms"][0]["reward"])
        porcentagem_prize = points / quizzes_count * 100
        value = (quizzes_reward * porcentagem_prize / 100)

        user = memberstack.get_member(user_id)
        if not user.get("member"):
            return logging.error(f"{user_id} not found.")

        database.User.get_or_create(
            id=user_id, 
            email=user["member"]["email"]
        )
        
        database.Reward.create(
            id=reward_id,
            user=user_id,
            value=value,
            status="created",
            classroom=classroom
        )

    reward_id = uuid4()
    reward = database.Reward.select(database.Reward.id).where(
                (database.Reward.user == user_id) & 
                (database.Reward.classroom == classroom))
    if not reward.exists():    
        background_tasks.add_task(
            func=create_reward, 
            user_id=user_id, 
            reward_id=reward_id
        )
    else:
        reward_id = reward.get().id
    
    lnurlw = lnurl.lnurl_encode(f"{API_DNS}/withdraw/api/v1/lnurl/{user_id}/{reward_id}")
    return JSONResponse({ "lnurl": lnurlw })

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