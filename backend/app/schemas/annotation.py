from pydantic import BaseModel, ConfigDict
from typing import Optional, Any

class AnnotationBase(BaseModel):
    class_label: str
    confidence: float
    geometry: Any

class AnnotationCreate(AnnotationBase):
    pass

class Annotation(AnnotationBase):
    id: int
    image_id: int
    annotation_type: str

    model_config = ConfigDict(from_attributes=True)
    