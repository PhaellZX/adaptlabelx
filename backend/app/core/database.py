from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.base import Base

# Troque para a URL do seu PostgreSQL quando for para produção
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Usando SQLite para simplicidade inicial

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Função para obter a sessão do banco de dados em cada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()