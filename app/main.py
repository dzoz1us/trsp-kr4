# app/main.py
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional
from itertools import count
from threading import Lock

# Импортируем пользовательские исключения
from app.exceptions import CustomExceptionA, CustomExceptionB
from app.schemas import ErrorResponse, UserData

app = FastAPI(title="My Test App")

# --- Хранилище пользователей в памяти ---
db: dict[int, dict] = {}
_id_seq = count(start=1)
_id_lock = Lock()

def next_user_id() -> int:
    with _id_lock:
        return next(_id_seq)

class UserIn(BaseModel):
    username: str
    age: int
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    age: int
    email: str

# --- Обработчики исключений ДОЛЖНЫ БЫТЬ ДО ЭНДПОИНТОВ ---

# Обработчик для CustomExceptionA
@app.exception_handler(CustomExceptionA)
async def custom_a_handler(request: Request, exc: CustomExceptionA):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Обработчик для CustomExceptionB
@app.exception_handler(CustomExceptionB)
async def custom_b_handler(request: Request, exc: CustomExceptionB):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Обработчик ошибок валидации
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )

# --- Эндпоинты ---

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/check-value/{value}")
async def check_value(value: int):
    if value < 0:
        raise CustomExceptionA(detail="Value cannot be negative!")
    return {"value": value, "status": "ok"}

@app.get("/product/{product_id}")
async def get_product(product_id: int):
    raise CustomExceptionB(detail=f"Product with ID {product_id} not found")

@app.post("/users/")
async def create_user(user: UserData):
    return {"message": "User created", "user": user}

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn):
    user_id = next_user_id()
    db[user_id] = user.model_dump()
    return {"id": user_id, **db[user_id]}

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **db[user_id]}

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if db.pop(user_id, None) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return Response(status_code=204)