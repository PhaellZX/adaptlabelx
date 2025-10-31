from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.base import Base
from app.core.config import settings 

# Usar a URL do objeto settings
engine = create_engine(settings.DATABASE_URL, pool_recycle=1800)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()