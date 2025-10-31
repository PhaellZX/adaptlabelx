# backend/tests/test_users.py
from fastapi.testclient import TestClient

# Não precisamos de importar 'client', o pytest injeta-o a partir do conftest.py

def test_create_user(client: TestClient):
    """
    Testa a criação de um novo utilizador com sucesso.
    """
    response = client.post(
        "/users/",
        json={"email": "testuser@example.com", "password": "testpassword123"},
    )
    
    assert response.status_code == 201 
    
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["is_active"] is True
    assert "hashed_password" not in data
    assert "password" not in data

def test_create_duplicate_user(client: TestClient):
    """
    Testa a falha ao tentar criar um utilizador com um email que já existe.
    """
    response = client.post(
        "/users/",
        json={"email": "testuser@example.com", "password": "anotherpassword"},
    )
    
    assert response.status_code == 400
    
    data = response.json()
    
    # --- ESTA É A CORREÇÃO ---
    # Verificar a mensagem de erro em Português
    assert data["detail"] == "Email já registrado."
    # --- FIM DA CORREÇÃO ---