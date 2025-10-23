from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.core.base import Base
from app.api.endpoints import users, auth, datasets, models, custom_models
from app.models import user, dataset, annotation, custom_model
from fastapi.staticfiles import StaticFiles

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

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# -------------- ROTAS -------------- #
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])
app.include_router(models.router, prefix="/models", tags=["Models"])
app.include_router(custom_models.router, prefix="/custom-models", tags=["Custom Models"])

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do AdaptlabelX!"}