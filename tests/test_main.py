# tests/test_main.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from faker import Faker
from app.main import app, db

fake = Faker()

@pytest_asyncio.fixture  # ← Изменил здесь
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
def clean_db():
    """Очистка хранилища перед каждым тестом"""
    db.clear()
    yield

# --- Тесты ---

@pytest.mark.asyncio
async def test_create_user_success(async_client: AsyncClient):
    user_data = {
        "username": fake.user_name(),
        "age": fake.random_int(min=18, max=99),
        "email": fake.email(),
        "password": fake.password(length=12)
    }
    response = await async_client.post("/users", json=user_data)
    assert response.status_code == 201
    resp_json = response.json()
    assert resp_json["username"] == user_data["username"]
    assert "id" in resp_json

@pytest.mark.asyncio
async def test_create_user_invalid_data(async_client: AsyncClient):
    user_data = {
        "username": fake.user_name(),
        "age": 25,
        "password": "short"
    }
    response = await async_client.post("/users", json=user_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_user_success(async_client: AsyncClient):
    user_data = {
        "username": fake.user_name(),
        "age": 30,
        "email": fake.email(),
        "password": fake.password()
    }
    create_response = await async_client.post("/users", json=user_data)
    user_id = create_response.json()["id"]
    
    get_response = await async_client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    assert get_response.json()["username"] == user_data["username"]

@pytest.mark.asyncio
async def test_get_user_not_found(async_client: AsyncClient):
    response = await async_client.get("/users/9999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_user_success(async_client: AsyncClient):
    user_data = {
        "username": fake.user_name(),
        "age": 30,
        "email": fake.email(),
        "password": fake.password()
    }
    create_response = await async_client.post("/users", json=user_data)
    user_id = create_response.json()["id"]
    
    delete_response = await async_client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204
    
    get_response = await async_client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_user_not_found(async_client: AsyncClient):
    response = await async_client.delete("/users/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_user_twice(async_client: AsyncClient):
    """Повторное удаление - должно быть 404"""
    user_data = {
        "username": fake.user_name(),
        "age": 30,
        "email": fake.email(),
        "password": fake.password()
    }
    create_response = await async_client.post("/users", json=user_data)
    user_id = create_response.json()["id"]
    
    # Первое удаление
    response1 = await async_client.delete(f"/users/{user_id}")
    assert response1.status_code == 204
    
    # Второе удаление
    response2 = await async_client.delete(f"/users/{user_id}")
    assert response2.status_code == 404