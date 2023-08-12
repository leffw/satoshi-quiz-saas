from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from uuid import uuid4

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
    points: int
    
    @validator("user")
    def validator_user(cls, user: str):
        if not user or str(user) == "null":
            return str(uuid4())
        else:
            return user
