from pydantic import BaseModel, EmailStr

class QuizSchema(BaseModel):
    answers: str