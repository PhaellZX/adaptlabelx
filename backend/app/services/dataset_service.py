import os
import shutil
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import List
from app.services import ia_service

from app.models.dataset import Dataset, Image
from app.schemas.dataset import DatasetCreate
import io              
import zipfile

# Define o diretório base para os uploads
UPLOAD_DIRECTORY = "uploads"

# --- Funções de Gerenciamento de Dataset ---

def create_dataset(db: Session, dataset: DatasetCreate, owner_id: int):
    """Cria um novo dataset no banco de dados."""
    db_dataset = Dataset(**dataset.model_dump(), owner_id=owner_id)
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

def get_dataset(db: Session, dataset_id: int):
    """Busca um único dataset pelo ID."""
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()

def get_datasets_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    """Lista os datasets de um usuário específico."""
    return db.query(Dataset).filter(Dataset.owner_id == owner_id).offset(skip).limit(limit).all()

def delete_dataset(db: Session, db_dataset: Dataset):
    """Deleta um dataset e sua pasta de imagens associada."""
    dataset_id = db_dataset.id
    db.delete(db_dataset)
    db.commit()
    
    # Remove a pasta de uploads do dataset
    dataset_path = os.path.join(UPLOAD_DIRECTORY, str(dataset_id))
    if os.path.isdir(dataset_path):
        shutil.rmtree(dataset_path)
    return True # Retorna sucesso

# --- Funções de Gerenciamento de Imagens ---

def save_image_files(db: Session, files: List[UploadFile], dataset_id: int):
    """Salva os arquivos de imagem no disco e cria os registros no banco."""
    
    # Cria a pasta para o dataset, se não existir
    dataset_path = os.path.join(UPLOAD_DIRECTORY, str(dataset_id))
    os.makedirs(dataset_path, exist_ok=True)
    
    saved_images = []
    for file in files:
        file_location = os.path.join(dataset_path, file.filename)
        
        # Salva o arquivo no disco
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        
        # Cria o registro no banco de dados
        db_image = Image(
            file_path=file_location,
            file_name=file.filename,
            dataset_id=dataset_id
        )
        db.add(db_image)
        saved_images.append(db_image)
    
    db.commit()
    for img in saved_images:
        db.refresh(img) # Garante que temos o ID da imagem
        
    return saved_images

# --- Função de Anotação com IA ---
def annotate_dataset_images(db: Session, dataset_id: int):
    """
    Função de trabalho que será executada em segundo plano.
    Ela busca todas as imagens de um dataset e aplica o modelo de IA.
    """
    print(f"Iniciando anotação para o dataset ID: {dataset_id}")
    db_dataset = get_dataset(db, dataset_id=dataset_id)
    if not db_dataset:
        print(f"Dataset {dataset_id} não encontrado. Abortando.")
        return

    for image in db_dataset.images:
        print(f"Processando imagem: {image.file_path}")
        try:
            results = ia_service.run_model_on_image(image.file_path, db_dataset.annotation_type)
            ia_service.create_annotations_from_results(db, db_image=image, results=results, annotation_type=db_dataset.annotation_type)
            print(f"Anotações salvas para a imagem ID: {image.id}")
        except Exception as e:
            print(f"Erro ao processar a imagem {image.id}: {e}")

    print(f"Processo de anotação concluído para o dataset ID: {dataset_id}")

def export_annotations_yolo(db: Session, db_dataset: Dataset):
    """
    Gera um arquivo ZIP na memória com as anotações no formato YOLO.
    """
    # 1. Criar um mapa de classes para IDs numéricos (ex: 'person': 0, 'car': 1)
    class_labels = sorted({ann.class_label for img in db_dataset.images for ann in img.annotations})
    class_map = {label: i for i, label in enumerate(class_labels)}

    # Objeto para simular um arquivo na memória RAM
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        # 2. Criar o arquivo 'classes.txt'
        classes_content = "\n".join(class_labels)
        zip_file.writestr('classes.txt', classes_content)

        # 3. Criar um arquivo .txt para cada imagem
        for image in db_dataset.images:
            if not image.annotations:
                continue # Pula imagens sem anotações

            # Remove a extensão do nome do arquivo original (ex: 'img.png' -> 'img')
            base_filename = os.path.splitext(image.file_name)[0]
            yolo_filename = f'{base_filename}.txt'

            yolo_content = []
            for ann in image.annotations:
                class_id = class_map[ann.class_label]
                geo = ann.geometry # O geometry já está normalizado
                line = f"{class_id} {geo['x']} {geo['y']} {geo['width']} {geo['height']}"
                yolo_content.append(line)
            
            zip_file.writestr(yolo_filename, "\n".join(yolo_content))
    
    # Retorna o buffer com o conteúdo do ZIP para ser enviado na resposta
    return zip_buffer.getvalue()