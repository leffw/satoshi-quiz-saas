from src.interfaces.api.schemas import QuizSchema
from playhouse.shortcuts import model_to_dict
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request, HTTPException
from src import database

import logging

router = APIRouter()

@router.post("/api/v1/quiz")
def create_quiz(data: QuizSchema, request: Request):
    """
    Create a new quiz for the user.

    Args:
        data (QuizSchema): The data containing the quiz information.
        request (Request): The FastAPI request object.

    Returns:
        JSONResponse: A JSON response containing the id of the created quiz.

    Raises:
        HTTPException: If the quiz creation fails or there is a server error.
    """
    user_id = request.data["id"]
    quiz_id = str(database.Quiz.get_or_create(
        user=user_id,
        topic=data.topic,
        prize=data.prize
    )[0].id)
    
    database.Quizzes.insert_many([{
        "quiz": quiz_id,
        "question": quiz.question, 
        "options": "|".join(quiz.options),
        "answer": quiz.answer,
        } for quiz in data.quizzes
    ]).execute()
    
    return JSONResponse({ "id":  quiz_id }, status_code=201)

@router.delete("/api/v1/quiz/{id}")
def delete_quiz(id: str, request: Request):
    """
    Delete a quiz with the given id belonging to the user.

    Args:
        id (str): The id of the quiz to be deleted.
        request (Request): The FastAPI request object.

    Returns:
        JSONResponse: A JSON response indicating the success of the operation or an error.

    Raises:
        HTTPException: If the quiz deletion fails, the quiz doesn't exist, or there is a server error.
    """
    user_id = request.data["id"]
    if not database.Quiz.select(database.Quiz.id).where(
        (database.Quiz.user == user_id) & 
        (database.Quiz.id == id)).exists():
        raise HTTPException(204)

    try:
        database.Quizzes.delete().where((database.Quizzes.quiz == id)).execute()
        database.Quiz.delete().where((database.Quiz.id == id)).execute()
        return JSONResponse({ "message": "Quiz deleted successfully" })
    except Exception as error:
        logging.error(str(error), exc_info=True)
        raise HTTPException(500, "It was not possible to delete the quiz.")

@router.get("/api/v1/public/quiz/{id}")
def get_quiz_by_id(id: str):
    """
    Get a quiz by its id.

    Args:
        id (str): The id of the quiz to retrieve.

    Returns:
        list: A list of dictionaries containing the quiz information.

    Raises:
        HTTPException: If the quiz with the given id doesn't exist.
    """    
    quizzes = []
    for quiz in (database.Quizzes
             .select()
             .where((database.Quizzes.quiz == id))):
        quiz = model_to_dict(quiz)
        quiz["created_at"] = quiz["created_at"].timestamp()
        quiz["updated_at"] = quiz["updated_at"].timestamp()
        del quiz["quiz"]
        quizzes.append(quiz)

    quiz = database.Quiz.select().where(
        (database.Quiz.id == id)).get()
    return { 
        "id": id, 
        "topic": quiz.topic, 
        "prize": quiz.prize, 
        "quizzes": quizzes, 
        "created_at": quiz.created_at.timestamp(),
        "updated_at": quiz.updated_at.timestamp() 
    }

@router.get("/api/v1/quizzes")
def get_list_quizzes(page: int = 1, size: int = 5, request: Request = Request):
    """
    Get a list of quizzes belonging to the user.

    Args:
        page (int, optional): The page number. Defaults to 1.
        size (int, optional): The number of quizzes per page. Defaults to 5.
        request (Request, optional): The FastAPI request object.

    Returns:
        list: A list of dictionaries containing the quiz information.

    Raises:
        HTTPException: If the page size is too large.
    """
    user_id = request.data["id"]
    if size > 5:
        raise HTTPException(400, "Size is too large.")

    quizzes = []
    for quiz in (database.Quiz
             .select()
             .where((database.Quiz.user == user_id))
             .order_by(database.Quiz.created_at.desc())
             .limit(size)
             .paginate(page, size)):
        quiz = model_to_dict(quiz)
        quiz["created_at"] = quiz["created_at"].timestamp()
        quiz["updated_at"] = quiz["updated_at"].timestamp()
        del quiz["user"]
        quizzes.append(quiz)

    return quizzes
