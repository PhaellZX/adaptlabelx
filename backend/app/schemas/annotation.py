from pydantic import BaseModel
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

    class Config:
        from_attributes = True