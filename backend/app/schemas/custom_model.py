from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)