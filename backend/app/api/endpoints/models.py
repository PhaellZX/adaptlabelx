# backend/app/api/endpoints/models.py
from fastapi import APIRouter
from typing import Dict
from app.services.ia_service import detection_model # Vamos pegar as classes do nosso modelo

router = APIRouter()

@router.get("/available-classes", response_model=Dict[int, str])
def get_available_classes():
    """
    Retorna o mapa de classes (ID e nome) que os modelos pré-treinados conhecem.
    """
    # detection_model.names é um dicionário como {0: 'person', 1: 'bicycle', ...}
    return detection_model.names