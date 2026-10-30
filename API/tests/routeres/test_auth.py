# API/tests/routers/test_auth.py
import pytest

# Nota: El 'client' se inyecta automáticamente desde el conftest.py

def test_register_user_success(client):
    """
    Test 1 (Rojo -> Verde): Validar que el registro automático 
    de FastAPI Users devuelva 201 y el JSON del usuario creado.
    """
    payload = {
        "email": "testuser@example.com",
        "password": "PasswordSeguro123!",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False
    }
    
    # Por defecto, FastAPI Users suele registrar en /auth/register
    # Ajusta la URL si en tus routers le pusiste un prefijo diferente (ej: /api/v1/auth/register)
    response = client.post("/auth/register", json=payload)
    
    assert response.status_code == 201
    
    data = response.json()
    assert "id" in data
    assert data["email"] == "testuser@example.com"
    assert data["is_active"] is True


def test_register_user_duplicate_email(client):
    """
    Test 2: Validar que intentar registrar el mismo email 
    devuelva un error 400 Bad Request estructurado.
    """
    payload = {
        "email": "duplicate@example.com",
        "password": "PasswordSeguro123!"
    }
    
    # Primer registro exitoso
    client.post("/auth/register", json=payload)
    
    # Segundo registro con el mismo email
    response = client.post("/auth/register", json=payload)
    
    assert response.status_code == 400
    assert response.json() == {"detail": "REGISTER_USER_ALREADY_EXISTS"}


def test_login_success(client):
    """
    Test 3: Validar que el login por OAuth2 (Form Data) devuelva 
    el token de acceso correctamente al autenticarse.
    """
    # 1. Creamos el usuario primero para poder loguearnos
    register_payload = {
        "email": "login@example.com",
        "password": "PasswordSeguro123!"
    }
    client.post("/auth/register", json=register_payload)
    
    # 2. FastAPI Users usa la especificación OAuth2, requiere enviar los datos como Form Data (data=), no como JSON.
    login_data = {
        "username": "login@example.com",
        "password": "PasswordSeguro123!"
    }
    
    # Por defecto el endpoint de login suele ser /auth/jwt/login o /auth/login
    response = client.post("/auth/jwt/login", data=login_data)
    
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    """
    Test 4: Validar el fallo de autenticación con credenciales erróneas.
    """
    login_data = {
        "username": "nonexistent@example.com",
        "password": "WrongPassword!"
    }
    
    response = client.post("/auth/jwt/login", data=login_data)
    
    assert response.status_code == 400
    assert response.json() == {"detail": "LOGIN_BAD_CREDENTIALS"}
