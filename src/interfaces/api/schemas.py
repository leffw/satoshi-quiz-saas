from pydantic import BaseModel, EmailStr
from typing import List, Optional

class MemberStackSchema(BaseModel):
    key: str

class LndhubSchema(BaseModel):
    url: str
    username: str
    password: str

class QuizzesSchema(BaseModel):
    question: str
    options: list
    answer: str

class QuizSchema(BaseModel):
    topic: str
    prize: int
    redirect: Optional[str]
    quizzes: List[QuizzesSchema]

class QuizAnswer(BaseModel):
    user: Optional[str]
    answers: str
