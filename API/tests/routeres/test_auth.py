import pytest

pytestmark = pytest.mark.anyio


async def test_register_user_success(client):
    payload = {
        "email": "testuser@example.com",
        "password": "PasswordSeguro123!",
        "name": "Test User",
    }

    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["email"] == "testuser@example.com"
    assert data["name"] == "Test User"
    assert data["is_active"] is True
    assert data["is_superuser"] is False
    assert data["is_verified"] is False


async def test_register_user_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "PasswordSeguro123!",
        "name": "Duplicate User",
    }

    first_response = await client.post("/auth/register", json=payload)
    assert first_response.status_code == 201

    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "REGISTER_USER_ALREADY_EXISTS"}


async def test_login_success(client):
    register_payload = {
        "email": "login@example.com",
        "password": "PasswordSeguro123!",
        "name": "Login User",
    }
    register_response = await client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 201

    login_data = {
        "username": "login@example.com",
        "password": "PasswordSeguro123!",
    }

    response = await client.post("/auth/jwt/login", data=login_data)

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_invalid_credentials(client):
    login_data = {
        "username": "nonexistent@example.com",
        "password": "WrongPassword!",
    }

    response = await client.post("/auth/jwt/login", data=login_data)

    assert response.status_code == 400
    assert response.json() == {"detail": "LOGIN_BAD_CREDENTIALS"}


async def test_current_user_with_jwt(client):
    register_payload = {
        "email": "jwt@example.com",
        "password": "PasswordSeguro123!",
        "name": "JWT User",
    }
    register_response = await client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 201

    login_response = await client.post(
        "/auth/jwt/login",
        data={
            "username": "jwt@example.com",
            "password": "PasswordSeguro123!",
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "jwt@example.com"
