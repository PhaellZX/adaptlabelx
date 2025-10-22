from pydantic import BaseModel
from typing import List, Optional
from .annotation import Annotation

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

class DatasetUpdate(DatasetBase):
    pass

class Dataset(DatasetBase):
    id: int
    owner_id: int
    images: List[Image] = [] # Retorna a lista de imagens junto com o dataset

    class Config:
        from_attributes = True