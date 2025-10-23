from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.base import Base
from app.models.custom_model import CustomModel

class Dataset(Base):
    __tablename__ = "datasets"

    selected_classes = Column(JSON, nullable=True)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    annotation_type = Column(String, nullable=False, default="detection")
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="datasets")
    
    # Se um dataset for deletado, todas as imagens associadas também serão.
    images = relationship("Image", back_populates="dataset", cascade="all, delete-orphan")

    custom_model_id = Column(Integer, ForeignKey("custom_models.id"), nullable=True)
    custom_model = relationship("CustomModel")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    dataset = relationship("Dataset", back_populates="images")

    annotations = relationship("Annotation", back_populates="image", cascade="all, delete-orphan")