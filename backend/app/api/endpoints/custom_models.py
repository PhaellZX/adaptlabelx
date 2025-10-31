from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.custom_model import CustomModel, CustomModelCreate
from app.services import custom_model_service

router = APIRouter()

@router.post("/", response_model=CustomModel, status_code=status.HTTP_201_CREATED)
def upload_new_model(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    name: str = Form(...),
    model_type: str = Form(...), # 'detection' ou 'segmentation'
    file: UploadFile = File(...)
):
    """
    Faz o upload de um novo modelo (.pt) para o usuário logado.
    """
    if not file.filename.endswith((".pt", ".pth")):
        raise HTTPException(status_code=400, detail="Tipo de arquivo inválido. Apenas arquivos .pt ou .pth são permitidos.")
    
    model_in = CustomModelCreate(name=name, model_type=model_type)
    
    model = custom_model_service.create_model(
        db=db, model_in=model_in, file=file, owner_id=current_user.id
    )
    return model

@router.get("/", response_model=List[CustomModel])
def read_user_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os modelos customizados do usuário logado.
    (Esta é a rota que o seu Modal vai chamar)
    """
    
    return custom_model_service.get_models_by_owner(db=db, owner_id=current_user.id)

@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Apaga um modelo customizado do usuário logado.
    """

    custom_model_service.delete_model(db=db, model_id=model_id, owner_id=current_user.id)
    return {"message": "Modelo apagado com sucesso."} # O status 204 não devolve corpo
