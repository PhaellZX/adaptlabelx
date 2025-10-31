# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app # Importa a sua app principal
from app.core.database import get_db, Base

# --- ESTA É A CORREÇÃO ---
# Importar os seus modelos a partir de 'app.models' (como no seu main.py)
from app.models import user, dataset, annotation, custom_model
# --- FIM DA CORREÇÃO ---


# --- 1. Configurar a Base de Dados de Teste (SQLite em memória) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, # Requerido pelo SQLite
    poolclass=StaticPool, # Usa um pool estático para testes
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 2. Criar as tabelas na BD de teste ---
# (Agora o 'Base' conhece os seus modelos graças à importação correta)
Base.metadata.create_all(bind=engine)

# --- 3. Criar a "falsa" função get_db para os testes ---
def override_get_db():
    """
    Uma versão de get_db que usa a base de dados de teste.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 4. Dizer à app FastAPI para USAR a nossa "falsa" BD ---
app.dependency_overrides[get_db] = override_get_db

# --- 5. Criar o "Cliente de Teste" ---
@pytest.fixture(scope="module")
def client():
    """
    Disponibiliza um TestClient para os nossos testes.
    """
    with TestClient(app) as c:
        yield c