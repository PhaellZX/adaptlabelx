# backend/app/api/endpoints/users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user 
from app.schemas.user import User, UserCreate
from app.services import user_service
from app.core.database import get_db

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint para registrar um novo usuário.
    """
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já registrado.",
        )
    return user_service.create_user(db=db, user=user)

# NOVA ROTA PROTEGIDA
@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Endpoint para obter as informações do usuário logado.
    """
    # A mágica acontece no 'Depends(get_current_user)'.
    # Se o token for inválido, o código nem chega a ser executado.
    # Se for válido, 'current_user' conterá o objeto do usuário.
    return current_user