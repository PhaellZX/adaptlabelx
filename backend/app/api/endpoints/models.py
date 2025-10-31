# backend/app/api/endpoints/models.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.core.database import get_db

# --- A CORREÇÃO ESTÁ AQUI ---
# O seu ficheiro chama-se 'dependencies.py', não 'deps.py'.
# Vamos importá-lo com o nome correto e dar-lhe o "apelido" (as deps)
from app.api import dependencies as deps # Para obter o utilizador logado
# --- FIM DA CORREÇÃO ---

from app.models.user import User
from app.services import custom_model_service # Para buscar os modelos customizados

# Este é o "contrato" que o frontend (React) espera receber
class ModelOptionSchema(BaseModel):
    id: str | int # O ID pode ser um nome (ex: 'yolov8n') ou um número (ex: 1)
    name: str
    
    # Adicionar esta configuração para Pydantic v2 (corrige os warnings)
    class Config:
        from_attributes = True

router = APIRouter()

# --- ESTE É O ENDPOINT QUE ESTAVA A FALTAR (e a causar o 404) ---
@router.get(
    "/", 
    response_model=List[ModelOptionSchema],
    summary="Listar todos os modelos disponíveis (Padrão e Customizados)"
)
def get_available_models(
    db: Session = Depends(get_db),
    # Esta linha agora vai funcionar porque 'deps' existe
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