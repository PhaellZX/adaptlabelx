# backend/scripts/create_superuser.py
import sys
import os

# Adiciona o diretório raiz do projeto ao path do Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.user_service import create_user
from app.schemas.user import UserCreate

db = SessionLocal()

# --- CONFIGURE AQUI OS DADOS DO SEU SUPERUSUÁRIO ---
SUPERUSER_EMAIL = "admin@example.com"
SUPERUSER_PASSWORD = "adminpassword123"
# ---------------------------------------------------

print("Criando superusuário...")

user_in = UserCreate(email=SUPERUSER_EMAIL, password=SUPERUSER_PASSWORD)
user = create_user(db, user_in)

# Define o usuário como superuser e ativo
user.is_superuser = True
user.is_active = True

db.add(user)
db.commit()
db.refresh(user)

print(f"Superusuário '{user.email}' criado com sucesso!")

db.close()