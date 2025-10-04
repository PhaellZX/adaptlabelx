from pydantic import BaseModel, EmailStr, Field 
from datetime import datetime
from typing import Optional

# Propriedades compartilhadas por todos os schemas de usuário
class UserBase(BaseModel):
    email: EmailStr

# Schema para a criação de um usuário (recebido pela API)
class UserCreate(UserBase):
    
    password: str = Field(
        ..., # Os três pontos indicam que o campo é obrigatório
        min_length=8, 
        max_length=72,
        description="A senha do usuário deve ter entre 8 e 72 caracteres."
    )

# Schema para a leitura de um usuário (retornado pela API)
class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None