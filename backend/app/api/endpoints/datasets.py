# backend/app/api/endpoints/datasets.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks 
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.dataset import Dataset, DatasetCreate, Image
from app.services import dataset_service

router = APIRouter()

@router.post("/", response_model=Dataset, status_code=status.HTTP_201_CREATED)
def create_new_dataset(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dataset_in: DatasetCreate,
):
    """
    Cria um novo dataset para o usuário logado.
    """
    dataset = dataset_service.create_dataset(
        db=db, dataset=dataset_in, owner_id=current_user.id
    )
    return dataset

@router.get("/", response_model=List[Dataset])
def read_user_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Lista todos os datasets do usuário logado.
    """
    datasets = dataset_service.get_datasets_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return datasets

@router.get("/{dataset_id}", response_model=Dataset)
def read_dataset_by_id(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Obtém um dataset específico pelo ID.
    """
    dataset = dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    if dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não tem permissão para acessar este dataset")
    return dataset

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset_by_id(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deleta um dataset.
    """
    dataset = dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    if dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não tem permissão para deletar este dataset")
    
    dataset_service.delete_dataset(db, db_dataset=dataset)
    return

@router.post("/{dataset_id}/images/", response_model=List[Image])
def upload_images_to_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    files: List[UploadFile] = File(...),
):
    """
    Faz o upload de uma ou mais imagens para um dataset específico.
    """
    dataset = dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    if dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não tem permissão para adicionar imagens a este dataset")
    
    images = dataset_service.save_image_files(db, files=files, dataset_id=dataset_id)
    return images

@router.post("/{dataset_id}/annotate", status_code=status.HTTP_202_ACCEPTED)
def start_annotation_for_dataset(
    dataset_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Inicia o processo de anotação automática para todas as imagens de um dataset.
    Este processo é executado em segundo plano.
    """
    dataset = dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    if dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não tem permissão para anotar este dataset")
    
    # Adiciona a tarefa de longa duração para ser executada em segundo plano
    background_tasks.add_task(dataset_service.annotate_dataset_images, db, dataset_id)
    
    return {"message": "O processo de anotação foi iniciado em segundo plano."}