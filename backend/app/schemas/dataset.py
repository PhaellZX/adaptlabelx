from pydantic import BaseModel
from typing import List, Optional, Any
from .annotation import Annotation
from app.schemas.custom_model import CustomModel

# --- Schemas para Imagem ---
class ImageBase(BaseModel):
    file_name: str

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int
    file_path: str
    annotations: List[Annotation] = []

    class Config:
        from_attributes = True

# --- Schemas para Dataset ---
class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None

class DatasetCreate(DatasetBase):
    annotation_type: str = "detection"
    selected_classes: Optional[List[str]] = None
    custom_model_id: Optional[int] = None

class DatasetUpdate(DatasetBase):
    pass

class Dataset(DatasetBase):
    id: int
    owner_id: int
    images: List[Image] = [] # Retorna a lista de imagens junto com o dataset
    custom_model: Optional[CustomModel] = None

    class Config:
        from_attributes = True