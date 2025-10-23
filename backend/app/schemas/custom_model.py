# backend/app/schemas/custom_model.py
from pydantic import BaseModel
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

    class Config:
        from_attributes = True