# backend/app/schemas/dataset.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from .annotation import Annotation
# Não precisamos mais do CustomModel aqui, pois o model_id é uma string
# from app.schemas.custom_model import CustomModel # <--- REMOVIDO

# --- Schemas para Imagem ---
class ImageBase(BaseModel):
    file_name: str

class ImageCreate(ImageBase):
    pass

class Image(ImageBase):
    id: int
    file_path: str
    annotations: List[Annotation] = []

    model_config = ConfigDict(from_attributes=True)


# --- Schemas para Dataset ---
class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None

class DatasetCreate(DatasetBase):
    model_id: Optional[str] = None 
    classes_to_annotate: Optional[List[str]] = None

class DatasetUpdate(DatasetBase):
    pass

class Dataset(DatasetBase):
    id: int
    owner_id: int
    images: List[Image] = [] 
    
    # --- A CORREÇÃO ESTÁ AQUI ---
    # Remover o campo "fantasma" que não existe na tabela da BD
    # custom_model: Optional[CustomModel] = None # <--- REMOVIDO
    
    # Adicionar o model_id à resposta (para que o frontend saiba qual modelo foi salvo)
    model_id: Optional[str] = None 

    model_config = ConfigDict(from_attributes=True)