from src.interfaces.api.schemas import QuizAnswer
from src.lib.memberstack import MemberStack
from fastapi.responses import JSONResponse
from src.lib.lndhub import LndHub
from src.lib.lnurl import lnurl_encode
from src.configs import API_EXTERNAL
from fastapi import APIRouter, HTTPException
from base64 import b64decode
from src import database

import logging

router = APIRouter()

@router.get("/api/v1/lnurl/withdraw/{user}/{id}")
def lnurl_withdraw(user: str, id: str):
    """
    Generate an LNURL for withdrawal if a valid reward exists.

    Args:
        user (str): The user's identifier.
        id (str): The quiz identifier.

    Returns:
        JSONResponse: LNURL details if a valid reward exists, or an error message otherwise.
    """
    reward = database.Reward.select(database.Reward.value).where(
            (database.Reward.id == id) &
            (database.Reward.status == "created"))
    if not reward.exists():
        return JSONResponse({"status": "ERROR", "reason": "No reward found."})
    
    reward = reward.get()
    value = (reward.value * 1000)
    return JSONResponse({
        "tag": "withdrawRequest",
        "callback": f"{API_EXTERNAL}/api/v1/lnurl/withdraw/reedem",
        "k1": id, 
        "minWithdrawable": value, 
        "maxWithdrawable": value,
    })

@router.get("/api/v1/lnurl/withdraw/reedem")
def lnurl_reedem_withdraw(
        k1: str = None,
        pr: str = None
    ):
    """
    Redeem an LNURL withdrawal by processing the payment.

    Args:
        user (str): The user's identifier.
        k1 (str, optional): The k1 value from the LNURL withdrawal. (Default: None)
        pr (str, optional): The payment request for the LNURL withdrawal. (Default: None)

    Returns:
        JSONResponse: A response indicating whether the payment was successful or not.
            If successful, the status will be "OK"; otherwise, an error message will be provided.
    """
    reward = database.Reward.select().where(
            (database.Reward.id == k1) &
            (database.Reward.status == "created"))
    if not reward.exists():
        return JSONResponse({"status": "ERROR", "reason": "No reward found."})

    reward = reward.get()
    lndhub = database.Lndhub.select().where(
        (database.Lndhub.user == str(database.Quiz.select().where(
        (database.Quiz.id == reward.quiz)).get().user))).get()

    lndhub = LndHub(
        url=lndhub.url,
        username=lndhub.username,
        password=lndhub.password
    )
    
    try:
        invoice_value = lndhub.decode_invoice(pr)["num_satoshis"]
    except Exception as error:
        logging.error(str(error), exc_info=True)
        return JSONResponse({
            "status": "ERROR", "reason": "Invoice is invalid." })
    
    if reward.value != invoice_value: 
        return JSONResponse({
            "status": "ERROR", "reason": "Invoice is invalid" })

    reward.status = "pending"
    reward.save()
    
    try:
        payinvoice = lndhub.payinvoice(pr)
    except Exception as error:
        logging.error(str(error), exc_info=True)
        payinvoice = {}

    if not payinvoice.get("payment_preimage"):
        reward.status = "created"
        reward.save()        
        return JSONResponse({
            "status": "ERROR", "reason": "Failed payment." })
    else:
        reward.status = "settled"
        reward.save()             
        return JSONResponse({ "status": "OK" })

@router.post("/api/v1/reward/{id}")
def create_reward(id: str, data: QuizAnswer):
    """
    Create a reward for a given quiz and user based on quiz answers.

    Args:
        id (str): The quiz identifier.
        data (QuizAnswer): Quiz answers submitted by the user.

    Returns:
        JSONResponse: LNURL details for the created reward.
    """
    quiz = database.Quiz.select(database.Quiz.prize, database.Quiz.user).where(
        (database.Quiz.id == id))
    if not quiz.exists():
        raise HTTPException(204)
    else:
        quiz = quiz.get()
        quiz_user = quiz.user
        quiz_prize = quiz.prize

    reward = database.Reward.select().where((database.Reward.quiz == id))
    if reward.exists():
        reward = reward.get()
        if reward.status != "created":
            raise HTTPException(204)
        
        return JSONResponse({ "lnurl": lnurl_encode(
            f"{API_EXTERNAL}/api/v1/lnurl/withdraw/{data.user}/{reward.id}") })

    try:
        answers = b64decode(data.answers).decode("utf-8")
    except:
        answers = b64decode(data.answers).decode("latin-1")

    answers = list(set(answers.split("&")))
    total_answer = 0
    total_points = 0
    for answer in (database.Quizzes
             .select(database.Quizzes.answer)
             .where((database.Quizzes.quiz == id))):
        total_answer += 1
        if answer.answer in answers:
            total_points += 1

    if not total_points:
        raise HTTPException(204)
    
    member_key = database.MemberStack.select(database.MemberStack.key).where(
        (database.MemberStack.user == quiz_user))
    if member_key.exists():
        memberstack = MemberStack(api_key=member_key.get().key)
        if not memberstack.get_member(data.user).get("member"):
            raise HTTPException(204)

    value = (quiz_prize * (total_points / total_answer * 100) / 100)    
    lnurl = f"{API_EXTERNAL}/api/v1/lnurl/withdraw/{data.user}/"
    lnurl+= str(database.Reward.get_or_create(quiz=id, value=value, status="created")[0].id)
    return JSONResponse({ "lnurl": lnurl_encode(lnurl) })
