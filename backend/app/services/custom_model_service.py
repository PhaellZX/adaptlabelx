# backend/app/services/custom_model_service.py
import os
import shutil
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.custom_model import CustomModel
from app.schemas.custom_model import CustomModelCreate

# Define o diretório onde os modelos dos usuários serão salvos
UPLOAD_DIR = "custom_models_user"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def create_model(db: Session, *, model_in: CustomModelCreate, file: UploadFile, owner_id: int) -> CustomModel:
    """
    Salva um arquivo de modelo enviado e cria um registro no banco de dados.
    """
    # Garante que o nome do arquivo é seguro
    if ".." in file.filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido.")

    # Cria um subdiretório para o usuário para evitar conflitos de nome
    user_model_dir = os.path.join(UPLOAD_DIR, str(owner_id))
    os.makedirs(user_model_dir, exist_ok=True)

    file_path = os.path.join(user_model_dir, file.filename)

    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Um modelo com este nome já existe.")

    # Salva o arquivo no disco
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # Cria o registro no banco de dados
    db_model = CustomModel(
        name=model_in.name,
        model_type=model_in.model_type,
        file_path=file_path, # Salva o caminho relativo
        owner_id=owner_id
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def get_models_by_owner(db: Session, *, owner_id: int) -> List[CustomModel]:
    """
    Lista todos os modelos pertencentes a um usuário específico.
    """
    return db.query(CustomModel).filter(CustomModel.owner_id == owner_id).all()

def get_model(db: Session, *, model_id: int, owner_id: int) -> CustomModel:
    """
    Obtém um modelo específico, verificando se o usuário é o proprietário.
    """
    db_model = db.query(CustomModel).filter(CustomModel.id == model_id, CustomModel.owner_id == owner_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Modelo não encontrado ou acesso negado.")
    return db_model

def delete_model(db: Session, *, model_id: int, owner_id: int):
    """
    Exclui um modelo do banco de dados e do sistema de arquivos.
    """
    db_model = get_model(db=db, model_id=model_id, owner_id=owner_id)

    # Remove o arquivo do disco
    if os.path.exists(db_model.file_path):
        os.remove(db_model.file_path)

    # Remove do banco de dados
    db.delete(db_model)
    db.commit()
    return {"message": "Modelo excluído com sucesso"}