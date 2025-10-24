# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.base import Base
from app.core.config import settings # <--- 1. Importar 'settings'

# 2. Usar a URL do objeto settings
engine = create_engine(settings.DATABASE_URL, pool_recycle=1800)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# (Lembre-se que removemos os 'import models' daqui)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()