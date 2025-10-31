from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

from app.core.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="datasets")
    images = relationship("Image", back_populates="dataset", cascade="all, delete-orphan")
    
    model_id = Column(String, nullable=True) 

    classes_to_annotate = Column(ARRAY(String), nullable=True)


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_path = Column(String, unique=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))

    dataset = relationship("Dataset", back_populates="images")
    annotations = relationship("Annotation", back_populates="image", cascade="all, delete-orphan")