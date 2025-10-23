from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.base import Base

class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(Integer, primary_key=True, index=True)
    
    # Ex: 'detection', 'segmentation'
    annotation_type = Column(String, nullable=False, default="detection")
    
    # Ex: 'car', 'person', 'dog'
    class_label = Column(String, index=True) 
    
    # Coordenadas da anotação. Usamos JSON para ser flexível.
    # Para Bounding Box: {"x": 100, "y": 150, "width": 50, "height": 75}
    geometry = Column(JSON) 
    
    # Confiança do modelo na detecção
    confidence = Column(Float) 
    
    image_id = Column(Integer, ForeignKey("images.id"))
    image = relationship("Image", back_populates="annotations")