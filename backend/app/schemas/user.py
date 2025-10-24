# backend/app/schemas/user.py

from pydantic import BaseModel, EmailStr
from typing import Optional

# --- UserBase ---
# Campos que são comuns a todos os schemas de Utilizador
class UserBase(BaseModel):
    email: EmailStr

# --- UserCreate ---
# O que esperamos receber do frontend para criar um utilizador (Registo)
class UserCreate(UserBase):
    password: str

# --- UserUpdate ---
# O que esperamos receber para atualizar um utilizador (Admin)
class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# --- User ---
# O que devolvemos ao frontend (o nosso "response_model")
class User(UserBase):
    id: int
    is_active: bool       # <--- CAMPO ADICIONADO
    is_superuser: bool    # <--- CAMPO ADICIONADO

    class Config:
        # Permite ao Pydantic ler os dados a partir de um modelo SQLAlchemy
        from_attributes = True