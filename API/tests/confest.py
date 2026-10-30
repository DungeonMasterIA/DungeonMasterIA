# API/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.db import Base  # Asegúrate de que apunte a tu DeclarativeBase original
from app.core.db import get_db  # El middleware/dependencia que usas en tus rutas
from main import app

# 1. URL de la Base de Datos de pruebas en MySQL.
# Conectamos al contenedor 'fastapi_mysql' usando una base de datos dedicada a tests.
TEST_DATABASE_URL = "mysql+pymysql://root:secret@fastapi_mysql:3306/dungeon_master_test"

# 2. Crear el motor y la sesión para los tests
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Crea las tablas en la base de datos de pruebas antes de correr los tests
    y las destruye al finalizar toda la suite de pruebas.
    """
    # Crea las tablas (puedes usar esto o migraciones de Alembic si es complejo)
    Base.metadata.create_engine(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    yield  # Aquí es donde se ejecutan los tests
    
    # Al terminar todos los tests, limpiamos la base de datos de prueba
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """
    Fixture que proporciona una sesión de base de datos limpia para cada test.
    Al finalizar el test, revierte (rollback) los cambios para mantener el aislamiento.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """
    Fixture que reemplaza la dependencia 'get_db' original de FastAPI 
    por nuestra sesión de pruebas 'db_session' controlada.
    """
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    # Aplicamos el "dependency override" en FastAPI
    app.dependency_overrides[get_db] = _get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
        
    # Limpiamos las modificaciones de dependencias al terminar el test
    app.dependency_overrides.clear()
