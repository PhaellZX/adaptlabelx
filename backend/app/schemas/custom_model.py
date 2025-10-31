# backend/app/schemas/custom_model.py
from pydantic import BaseModel, ConfigDict # <--- 1. ADICIONAR O IMPORT DO CONFIGDICT
from typing import Optional

class CustomModelBase(BaseModel):
    name: str
    model_type: str # 'detection' ou 'segmentation'

class CustomModelCreate(CustomModelBase):
    pass

class CustomModel(CustomModelBase):
    id: int
    file_path: str
    owner_id: int

    # --- 2. ESTA É A CORREÇÃO PARA O PYDANTIC V2 ---
    # Trocamos "class Config:" por "model_config ="
    model_config = ConfigDict(from_attributes=True)
    # --- FIM DA CORREÇÃO ---