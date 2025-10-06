from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api.endpoints import users, auth, datasets
from app.models import user, dataset, annotation

# Cria todas as tabelas no banco de dados (em um cenário real, use Alembic para migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AdaptlabelX API")

# --- CONFIGURAÇÃO DO CORS --- #

# Lista de origens permitidas (endereços do seu frontend)
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# -------------- ROTAS -------------- #
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do AdaptlabelX!"}