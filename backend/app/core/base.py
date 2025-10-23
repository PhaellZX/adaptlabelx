# backend/app/core/base.py

from sqlalchemy.orm import declarative_base

# Este é o "pai" de todos os nossos modelos
Base = declarative_base()