# app/schemas.py
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str

class UserData(BaseModel):  
    username: str
    age: int
    email: str  
    password: str