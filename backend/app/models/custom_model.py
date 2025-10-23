# backend/app/models/custom_model.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import Base

class CustomModel(Base):
    __tablename__ = "custom_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    model_type = Column(String, nullable=False) # 'detection' ou 'segmentation'
    file_path = Column(String, nullable=False, unique=True) # Caminho no servidor
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")