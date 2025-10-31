from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db

from app.api import dependencies as deps

from app.models.user import User
from app.services import custom_model_service 

class ModelOptionSchema(BaseModel):
    id: str | int # O ID pode ser um nome (ex: 'yolov8n') ou um número (ex: 1)
    name: str
    
    class Config:
        from_attributes = True

router = APIRouter()

@router.get(
    "/", 
    response_model=List[ModelOptionSchema],
    summary="Listar todos os modelos disponíveis (Padrão e Customizados)"
)
def get_available_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Retorna uma lista combinada de modelos padrão (YOLO, SAM) 
    e modelos customizados enviados pelo utilizador.
    """
    
    # 1. Modelos Padrão (Hardcoded)
    standard_models = [
        ModelOptionSchema(id="yolov8n_det", name="YOLOv8n (Detecção)"),
        ModelOptionSchema(id="yolov8n_seg", name="YOLOv8n (Segmentação)"),
        ModelOptionSchema(id="sam", name="Segment Anything (SAM)"),
    ]
    
    # 2. Modelos Customizados (Buscados do banco de dados)
    custom_models = custom_model_service.get_models_by_owner(db, owner_id=current_user.id)
    
    # 3. Converter modelos customizados para o formato ModelOptionSchema
    custom_models_options = [
        ModelOptionSchema(id=model.id, name=f"{model.name} (Customizado)")
        for model in custom_models
    ]
    
    # 4. Combinar as listas e retornar
    return standard_models + custom_models_options