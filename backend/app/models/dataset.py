from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    annotation_type = Column(String, nullable=False, default="detection")
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="datasets")
    
    # Se um dataset for deletado, todas as imagens associadas também serão.
    images = relationship("Image", back_populates="dataset", cascade="all, delete-orphan")

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    dataset = relationship("Dataset", back_populates="images")

    annotations = relationship("Annotation", back_populates="image", cascade="all, delete-orphan")