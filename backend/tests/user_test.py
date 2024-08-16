import pytest
from httpx import AsyncClient
from backend.main import app
from src.app.core.schema.user import RegisterUserParam, AddUserParam, ResetPasswordParam, UpdateUserParam

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def user_data():
    return {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "test_password",
        "phone": "0502220903" 
    }

@pytest.fixture
def user_login_data():
    return {
        "email": "test@example.com",
        "password": "test_password"
    }

@pytest.mark.asyncio
async def test_pre_register_user(async_client, user_data):
    response = await async_client.post("/pre-register", params={"email": user_data["email"]})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_register_user(async_client, user_data):
    register_data = RegisterUserParam(**user_data)
    response = await async_client.post("/register", json=register_data.model_dump(), params={"code": "123456"})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_add_user(async_client, user_data):
    add_user_data = AddUserParam(**user_data, roles=["role1"], establishment_uuid="some-uuid")
    response = await async_client.post("/add", json=add_user_data.model_dump())
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_password_reset(async_client, user_login_data):
    reset_data = ResetPasswordParam(old_password="old_password", new_password="new_password", confirm_password="new_password")
    response = await async_client.post("/password/reset", json=reset_data.model_dump(), cookies={"access_token": "test_access_token"})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_get_current_user(async_client):
    response = await async_client.get("/me", cookies={"access_token": "test_access_token"})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_get_user(async_client, user_data):
    response = await async_client.get(f"/{user_data['email']}", cookies={"access_token": "test_access_token"})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_update_role(async_client, user_data):
    response = await async_client.put(f"/role/{user_data['email']}", json={"role_uuids": ["role1", "role2"]}, cookies={"access_token": "test_access_token"})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_update_user(async_client, user_data):
    update_data = UpdateUserParam(first_name="Updated", last_name="User", email=user_data["email"], phone=user_data["phone"])
    response = await async_client.put(f"/{user_data['email']}", json=update_data.model_dump(), cookies={"access_token": "test_access_token"})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_get_pagination_users(async_client):
    response = await async_client.get("/", cookies={"access_token": "test_access_token"}, params={"email": "test@example.com"})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_super_set(async_client):
    response = await async_client.put("/super", json={"pk": "user_id"}, cookies={"access_token": "test_access_token"})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_staff_set(async_client):
    response = await async_client.put("/staff", json={"pk": "user_id"}, cookies={"access_token": "test_access_token"})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_status_set(async_client):
    response = await async_client.put("/status", json={"pk": "user_id"}, cookies={"access_token": "test_access_token"})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_multi_set(async_client):
    response = await async_client.put("/multi", json={"pk": "user_id"}, cookies={"access_token": "test_access_token"})
    assert response.status_code == 200
    assert response.json()["code"] == 200

@pytest.mark.asyncio
async def test_delete_user(async_client, user_data):
    response = await async_client.delete(f"/{user_data['email']}", cookies={"access_token": "test_access_token"})
    assert response.status_code == 200
    assert response.json()["code"] == 200
