# backend/app/services/user_service.py

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.core.security import verify_password

def get_user_by_email(db: Session, email: str):
    """Busca um usuário pelo email."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    """Cria um novo usuário no banco de dados."""
    
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# NOVA FUNÇÃO DE AUTENTICAÇÃO
def authenticate_user(db: Session, email: str, password: str):
    """
    Autentica um usuário, verificando email e senha.
    Retorna o objeto do usuário se for bem-sucedido, senão False.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user