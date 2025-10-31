# backend/app/models/dataset.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY # <-- 1. IMPORTAR O TIPO ARRAY

from app.core.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="datasets")
    images = relationship("Image", back_populates="dataset", cascade="all, delete-orphan")
    
    # --- 2. ADICIONAR O CAMPO 'model_id' (SE AINDA NÃO EXISTIR) ---
    # Isto é o que liga ao modelo (ex: 'yolov8n_det' ou o ID de um modelo customizado)
    model_id = Column(String, nullable=True) 

    # --- 3. ADICIONAR A NOVA COLUNA PARA AS CLASSES ---
    # Isto irá armazenar a sua lista ['dog', 'cat']
    classes_to_annotate = Column(ARRAY(String), nullable=True)


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_path = Column(String, unique=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))

    dataset = relationship("Dataset", back_populates="images")
    annotations = relationship("Annotation", back_populates="image", cascade="all, delete-orphan")