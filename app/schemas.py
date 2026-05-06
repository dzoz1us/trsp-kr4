# app/schemas.py
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str

class UserData(BaseModel):  # Для Задания 10.2
    username: str
    age: int
    email: str  # Для простоты без EmailStr, но можно и с ним
    password: str