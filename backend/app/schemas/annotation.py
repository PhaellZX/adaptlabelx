# backend/app/schemas/annotation.py

from pydantic import BaseModel, ConfigDict # <--- 1. ADICIONAR O IMPORT DO CONFIGDICT
from typing import Optional, Any

class AnnotationBase(BaseModel):
    class_label: str
    confidence: float
    geometry: Any # estou usando 'Any' para aceitar qualquer estrutura JSON

class AnnotationCreate(AnnotationBase):
    pass

class Annotation(AnnotationBase):
    id: int
    image_id: int
    annotation_type: str

    # --- 2. ESTA É A CORREÇÃO PARA O PYDANTIC V2 ---
    # Trocamos "class Config:" por "model_config ="
    model_config = ConfigDict(from_attributes=True)
    # --- FIM DA CORREÇÃO ---