import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import engine, Base
# Importar todos os seus endpoints
from app.api.endpoints import users, auth, datasets, models, custom_models
# Importar os seus modelos da BD para que o create_all funcione
from app.models import user, dataset, annotation, custom_model

# Criar tabelas (Isto agora vai criar as tabelas corrigidas)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AdaptLabelX API")

# Criar a pasta 'uploads' se ela não existir
os.makedirs("uploads", exist_ok=True)

# Montar o diretório 'uploads' para ser servido publicamente
# Agora, o pedido do Nginx para "http://backend:8000/uploads/file.png"
# irá servir o ficheiro "backend/uploads/file.png"
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configuração do CORS (Middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos
    allow_headers=["*"], # Permite todos os headers
)

# Incluir os routers da API
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
app.include_router(custom_models.router, prefix="/custom-models", tags=["custom_models"])
app.include_router(models.router, prefix="/models", tags=["models"]) 

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API AdaptLabelX"}