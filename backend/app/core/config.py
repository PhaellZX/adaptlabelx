# backend/app/core/config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Garante que o .env é lido
load_dotenv() 

class Settings(BaseSettings):
    # Mapeia automaticamente as variáveis do .env
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        # Aponta para o .env na raiz do backend
        env_file = ".env" 

# Esta é a instância que todos os outros arquivos irão importar
settings = Settings()