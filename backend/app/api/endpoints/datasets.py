# backend/app/api/endpoints/datasets.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks 
from sqlalchemy.orm import Session
import os 
import io

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
# Corrigir imports (o schema de Imagem vem de dataset, o modelo vem de dataset)
from app.schemas.dataset import Dataset, DatasetCreate, Image as SchemaImage
from app.models.dataset import Image as ModelImage
from app.services import dataset_service
from app.services import ia_service 
from app.services.dataset_service import UPLOAD_DIRECTORY
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.post("/", response_model=Dataset, status_code=status.HTTP_201_CREATED)
def create_new_dataset(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dataset_in: DatasetCreate,
):
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
    datasets = dataset_service.get_datasets_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return datasets

@router.get("/{dataset_id}", response_model=Dataset)
def get_dataset_details(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_dataset = dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    if db_dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não autorizado")
    return db_dataset
    
@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset_service.delete_dataset(db=db, dataset_id=dataset_id, owner_id=current_user.id)
    return {"ok": True} 

@router.post("/{dataset_id}/images/", response_model=List[SchemaImage])
def upload_images_to_dataset(
    dataset_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_dataset = dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    if db_dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não autorizado")
    
    new_images = dataset_service.save_uploaded_images(
        db=db, db_dataset=db_dataset, files=files
    )
    return new_images

@router.post("/{dataset_id}/annotate", status_code=status.HTTP_202_ACCEPTED)
def start_annotation_route(
    dataset_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), # A sessão 'db' ainda é necessária para verificar as permissões
    current_user: User = Depends(get_current_user),
):
    """
    Inicia a tarefa de anotação (o "Gerente") em segundo plano.
    """
    db_dataset = dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    if db_dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não autorizado")

    # --- A CORREÇÃO DO BUG (Sessão Morta / TypeError) ---
    # O 'dataset_service.run_annotation_for_dataset' agora
    # cria a sua própria sessão, por isso NÃO passamos 'db'
    background_tasks.add_task(
        dataset_service.run_annotation_for_dataset, 
        dataset_id=dataset_id # <--- Removido o argumento 'db=db'
    )
    # --- FIM DA CORREÇÃO ---

    return {"message": "Processo de anotação iniciado em segundo plano."}


# --- Rotas de Exportação (O seu código original está perfeito) ---

@router.get("/{dataset_id}/export/yolo", response_class=StreamingResponse)
def export_dataset_annotations_yolo(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    if dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não tem permissão para acessar este dataset")

    zip_bytes = dataset_service.export_annotations_yolo(db, db_dataset=dataset)
    
    filename = f"{dataset.name.replace(' ', '_')}_yolo.zip"
    
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/{dataset_id}/export/labelme", response_class=StreamingResponse)
def export_dataset_annotations_labelme(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    if dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não tem permissão para acessar este dataset")

    zip_bytes = dataset_service.export_annotations_labelme(db, db_dataset=dataset)
    
    filename = f"{dataset.name.replace(' ', '_')}_labelme.zip"
    
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/{dataset_id}/export/coco", response_class=StreamingResponse)
def export_dataset_annotations_coco(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    if dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não tem permissão para acessar este dataset")

    zip_bytes = dataset_service.export_annotations_coco(db, db_dataset=dataset)
    
    filename = f"{dataset.name.replace(' ', '_')}_coco.zip"
    
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/{dataset_id}/export/cvat", response_class=StreamingResponse)
def export_dataset_annotations_cvat(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = dataset_service.get_dataset(db, dataset_id=dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    if dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Não tem permissão para acessar este dataset")

    zip_bytes = dataset_service.export_annotations_cvat(db, db_dataset=dataset)
    
    filename = f"{dataset.name.replace(' ', '_')}_cvat.zip"
    
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )