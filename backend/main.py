# backend/main.py

from fastapi import FastAPI
from app.core.database import engine, Base
from app.api.endpoints import users, auth

# Cria todas as tabelas no banco de dados (em um cenário real, use Alembic para migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AdaptlabelX API")

# Inclui o router de usuários na aplicação principal
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do AdaptlabelX!"}