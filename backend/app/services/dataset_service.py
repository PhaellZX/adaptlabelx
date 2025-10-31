import os
import shutil
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.services import ia_service

from app.models.dataset import Dataset, Image
from app.schemas.dataset import DatasetCreate
import io              
import zipfile
import json
from PIL import Image as PILImage
import datetime 
import numpy as np 
import xml.etree.ElementTree as ET 
from xml.dom import minidom 

# --- 1. ADICIONAR IMPORT PARA A SESSÃO "VIVA" ---
from app.core.database import SessionLocal

UPLOAD_DIRECTORY = "uploads"

# --- Funções de CRUD ---
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
    """Lista todos os datasets de um usuário."""
    return db.query(Dataset).filter(Dataset.owner_id == owner_id).offset(skip).limit(limit).all()

def save_uploaded_images(db: Session, db_dataset: Dataset, files: List[UploadFile]) -> List[Image]:
    """Salva os arquivos de imagem no disco e cria os registros no banco."""
    dataset_dir = os.path.join(UPLOAD_DIRECTORY, str(db_dataset.id))
    os.makedirs(dataset_dir, exist_ok=True)
    
    new_images = []
    for file in files:
        file_path = os.path.join(dataset_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        relative_path = os.path.join(str(db_dataset.id), file.filename) 
        
        db_image = Image(
            file_name=file.filename,
            file_path=relative_path, 
            dataset_id=db_dataset.id
        )
        db.add(db_image)
        new_images.append(db_image)
        
    db.commit()
    for img in new_images:
        db.refresh(img)
    return new_images

def delete_dataset(db: Session, dataset_id: int, owner_id: int):
    """Exclui um dataset e todas as suas imagens e anotações."""
    db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == owner_id).first()
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset não encontrado")
    
    dataset_dir = os.path.join(UPLOAD_DIRECTORY, str(dataset_id))
    if os.path.exists(dataset_dir):
        shutil.rmtree(dataset_dir)
        
    db.delete(db_dataset)
    db.commit()
    return True

# --- 2. FUNÇÃO "GERENTE" ---
def run_annotation_for_dataset(dataset_id: int): 
    """
    O "Gerente": Pega no dataset, faz o loop e chama o "Trabalhador de IA"
    com o filtro de classes correto.
    Esta função CRIA A SUA PRÓPRIA SESSÃO de BD.
    """
    print(f"Iniciando tarefa de anotação para dataset {dataset_id}")
    
    db = SessionLocal() # Cria uma nova sessão "viva"
    
    try:
        db_dataset = get_dataset(db, dataset_id=dataset_id)
        if not db_dataset or not db_dataset.model_id:
            print(f"Dataset {dataset_id} não encontrado ou sem modelo.")
            return

        # Busca as imagens que ainda não têm anotações
        images_to_annotate = db.query(Image).filter(
            Image.dataset_id == dataset_id,
            ~Image.annotations.any() 
        ).all()
        
        if not images_to_annotate:
            print(f"Não há imagens novas para anotar no dataset {dataset_id}.")
            return

        print(f"Anotando {len(images_to_annotate)} imagens...")

        for db_image in images_to_annotate:
            image_path = os.path.join(UPLOAD_DIRECTORY, db_image.file_path)
            if not os.path.exists(image_path):
                print(f"Imagem não encontrada: {image_path}")
                continue
                
            try:
                # Passar o owner_id para o "Trabalhador de IA"
                results = ia_service.run_model_on_image(
                    image_path=image_path,
                    model_type=db_dataset.model_id, 
                    selected_classes=db_dataset.classes_to_annotate,
                    owner_id=db_dataset.owner_id 
                )
                
                ia_service.create_annotations_from_results(
                    db, 
                    results, 
                    db_image, 
                    db_dataset.model_id,
                    owner_id=db_dataset.owner_id 
                )
                
                db.commit() 
                
            except Exception as e:
                print(f"Erro ao processar a imagem {db_image.file_name}: {e}")
                db.rollback() 

    except Exception as e:
        print(f"Erro geral na tarefa de anotação: {e}")
        db.rollback()
    finally:
        print(f"Tarefa de anotação concluída para o dataset {dataset_id}.")
        db.close() # Fecha a sessão "viva"

# --- Funções de Exportação ---

def export_annotations_yolo(db: Session, db_dataset: Dataset):
    zip_buffer = io.BytesIO()
    
    class_names = sorted(list(set(ann.class_label for img in db_dataset.images for ann in img.annotations)))
    class_map = {name: i for i, name in enumerate(class_names)}

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        yaml_content = f"names: {class_names}\nnc: {len(class_names)}\n"
        zip_file.writestr("data.yaml", yaml_content)
        
        for image in db_dataset.images:
            txt_filename = os.path.splitext(image.file_name)[0] + ".txt"
            txt_content = []
            
            for ann in image.annotations:
                if ann.annotation_type == 'detection': 
                    class_id = class_map[ann.class_label]
                    geo = ann.geometry
                    txt_content.append(f"{class_id} {geo['x']} {geo['y']} {geo['width']} {geo['height']}")

            if txt_content:
                zip_file.writestr(f"labels/{txt_filename}", "\n".join(txt_content))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def export_annotations_labelme(db: Session, db_dataset: Dataset):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for image in db_dataset.images:
            json_filename = os.path.splitext(image.file_name)[0] + ".json"
            
            try:
                img_path = os.path.join(UPLOAD_DIRECTORY, image.file_path)
                with PILImage.open(img_path) as img:
                    img_width, img_height = img.size
            except FileNotFoundError:
                img_width, img_height = 0, 0 
            
            labelme_data = {
                "version": "5.0.1",
                "flags": {},
                "shapes": [],
                "imagePath": image.file_name,
                "imageData": None, 
                "imageHeight": img_height,
                "imageWidth": img_width,
            }

            for ann in image.annotations:
                shape = {
                    "label": ann.class_label,
                    "group_id": None,
                    "flags": {},
                }
                
                if ann.annotation_type == 'segmentation':
                    shape["shape_type"] = "polygon"
    
                    points = [
                        [p[0] * img_width, p[1] * img_height] for p in ann.geometry
                    ]
                    shape["points"] = points
                
                elif ann.annotation_type == 'detection':
                    shape["shape_type"] = "rectangle"
                    geo = ann.geometry
                    x_min = (geo['x'] - geo['width'] / 2) * img_width
                    y_min = (geo['y'] - geo['height'] / 2) * img_height
                    x_max = (geo['x'] + geo['width'] / 2) * img_width
                    y_max = (geo['y'] + geo['height'] / 2) * img_height
                    shape["points"] = [[x_min, y_min], [x_max, y_max]]

                labelme_data["shapes"].append(shape)

            zip_file.writestr(json_filename, json.dumps(labelme_data, indent=2))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def export_annotations_coco(db: Session, db_dataset: Dataset):
    coco_data = {
        "info": {
            "description": db_dataset.name,
            "date_created": datetime.datetime.utcnow().isoformat()
        },
        "licenses": [],
        "images": [],
        "annotations": [],
        "categories": [],
    }

    class_names = sorted(list(set(ann.class_label for img in db_dataset.images for ann in img.annotations)))
    class_map = {name: i + 1 for i, name in enumerate(class_names)} 
    for name, class_id in class_map.items():
        coco_data["categories"].append({
            "id": class_id,
            "name": name,
            "supercategory": "object",
        })

    ann_id_counter = 1
    for image in db_dataset.images:
        try:
            img_path = os.path.join(UPLOAD_DIRECTORY, image.file_path)
            with PILImage.open(img_path) as img:
                img_width, img_height = img.size
        except FileNotFoundError:
            img_width, img_height = 0, 0
            
        image_info = {
            "id": image.id,
            "file_name": image.file_name,
            "width": img_width,
            "height": img_height,
        }
        coco_data["images"].append(image_info)

        for ann in image.annotations:
            class_id = class_map[ann.class_label]
            ann_info = {
                "id": ann_id_counter,
                "image_id": image.id,
                "category_id": class_id,
                "iscrowd": 0,
            }
            
            if ann.annotation_type == 'segmentation':
                segmentation_flat = []
                for p in ann.geometry:
                    segmentation_flat.extend([p[0] * img_width, p[1] * img_height])
                
                x_coords = [p[0] * img_width for p in ann.geometry]
                y_coords = [p[1] * img_height for p in ann.geometry]
                x_min = min(x_coords)
                y_min = min(y_coords)
                width = max(x_coords) - x_min
                height = max(y_coords) - y_min
                bbox = [x_min, y_min, width, height]
                area = width * height 
                
                ann_info["segmentation"] = [segmentation_flat]
                ann_info["bbox"] = bbox
                ann_info["area"] = area

            elif ann.annotation_type == 'detection':
                geo = ann.geometry
                width = geo['width'] * img_width
                height = geo['height'] * img_height
                x_min = (geo['x'] * img_width) - (width / 2)
                y_min = (geo['y'] * img_height) - (height / 2)
                bbox = [x_min, y_min, width, height]
                area = width * height
                
                ann_info["bbox"] = bbox
                ann_info["area"] = area
            
            coco_data["annotations"].append(ann_info)
            ann_id_counter += 1

    json_string = json.dumps(coco_data, indent=2)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("annotations.json", json_string)
        
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def export_annotations_cvat(db: Session, db_dataset: Dataset):
    root = ET.Element('annotations')
    ET.SubElement(root, 'version').text = '1.1'
    
    meta = ET.SubElement(root, 'meta')
    task = ET.SubElement(meta, 'task')
    ET.SubElement(task, 'name').text = db_dataset.name
    labels = ET.SubElement(task, 'labels')
    class_names = sorted(list(set(ann.class_label for img in db_dataset.images for ann in img.annotations)))
    for name in class_names:
        label = ET.SubElement(labels, 'label')
        ET.SubElement(label, 'name').text = name

    for image in db_dataset.images:
        try:
            img_path = os.path.join(UPLOAD_DIRECTORY, image.file_path)
            with PILImage.open(img_path) as img:
                img_width, img_height = img.size
        except FileNotFoundError:
            img_width, img_height = 0, 0
            
        image_element = ET.SubElement(root, 'image', id=str(image.id), name=image.file_name, width=str(img_width), height=str(img_height))
        
        for ann in image.annotations:
            ann_attrs = {
                "label": ann.class_label,
                "occluded": "0",
                "source": "model",
            }
            
            if ann.annotation_type == 'segmentation':
                points_list = []
                for p in ann.geometry: 
                    x_abs = p[0] * img_width
                    y_abs = p[1] * img_height
                    points_list.append(f"{x_abs:.2f},{y_abs:.2f}")
                points_str = ";".join(points_list)
                ann_attrs["points"] = points_str
                ET.SubElement(image_element, 'polygon', ann_attrs)

            else: # 'detection'
                geo = ann.geometry
                x_min = (geo['x'] - geo['width'] / 2) * img_width
                y_min = (geo['y'] - geo['height'] / 2) * img_height
                x_max = (geo['x'] + geo['width'] / 2) * img_width
                y_max = (geo['y'] + geo['height'] / 2) * img_height
                
                ann_attrs["xtl"] = f"{x_min:.2f}"
                ann_attrs["ytl"] = f"{y_min:.2f}"
                ann_attrs["xbr"] = f"{x_max:.2f}"
                ann_attrs["ybr"] = f"{y_max:.2f}"
                ET.SubElement(image_element, 'box', ann_attrs)
                
    xml_str = ET.tostring(root, 'utf-8')
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("annotations.xml", pretty_xml_str)
        
    zip_buffer.seek(0)
    return zip_buffer.getvalue()