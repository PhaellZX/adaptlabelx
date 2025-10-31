from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import User, UserCreate
from app.services import user_service
from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_active_superuser
from app.schemas.user import User, UserCreate, UserUpdate

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

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Endpoint para obter as informações do usuário logado.
    """
    # A mágica acontece no 'Depends(get_current_user)'.
    # Se o token for inválido, o código nem chega a ser executado.
    # Se for válido, 'current_user' conterá o objeto do usuário.
    return current_user

@router.get("/", response_model=List[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Lista todos os usuários. Apenas para superusuários.
    """
    users = user_service.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Obtém um usuário específico pelo ID. Apenas para superusuários.
    """
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user

@router.put("/{user_id}", response_model=User)
def update_user_by_id(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Atualiza um usuário. Apenas para superusuários.
    """
    db_user = user_service.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    user = user_service.update_user(db=db, db_user=db_user, user_in=user_in)
    return user

@router.delete("/{user_id}", response_model=User)
def delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
):
    """
    Deleta um usuário. Apenas para superusuários.
    """
    user = user_service.delete_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user