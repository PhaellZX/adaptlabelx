import os
import shutil
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from app.services import ia_service

from app.models.dataset import Dataset, Image
from app.schemas.dataset import DatasetCreate
import io              
import zipfile
import json
from PIL import Image as PILImage
import datetime # Adicionar para o campo 'info' do COCO
import numpy as np # Adicionar para cálculos de área e bbox
import xml.etree.ElementTree as ET # <--- 1. Adicionar import para XML
from xml.dom import minidom # Para formatar o XML (deixar "bonito")

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
    Inicia a anotação para todas as imagens num dataset.
    Isto agora irá verificar se um modelo customizado deve ser usado.
    """
    print(f"Iniciando anotação para o dataset ID: {dataset_id}")
    db_dataset = get_dataset(db, dataset_id=dataset_id)
    if not db_dataset:
        print("Dataset não encontrado, a anotação foi cancelada.")
        return

    # Obtém as configurações de anotação do dataset
    annotation_type = db_dataset.annotation_type
    selected_classes = db_dataset.selected_classes
    custom_model_path: Optional[str] = None
    
    # --- NOVA LÓGICA ---
    if db_dataset.custom_model_id and db_dataset.custom_model:
        # Se um modelo customizado está ligado a este dataset
        custom_model_path = db_dataset.custom_model.file_path
        # O tipo de anotação é ditado pelo modelo customizado
        annotation_type = db_dataset.custom_model.model_type
        print(f"Usando modelo customizado: {custom_model_path}")
    else:
        # Usa um modelo padrão
        print(f"Usando modelo padrão: {annotation_type}")
    # --- FIM DA NOVA LÓGICA ---

    for image in db_dataset.images:
        if not os.path.exists(image.file_path):
            print(f"Arquivo de imagem não encontrado, pulando: {image.file_path}")
            continue
        
        print(f"Processando imagem: {image.file_path}")
        try:
            # 1. Passa o custom_model_path para o serviço de IA
            results = ia_service.run_model_on_image(
                image.file_path, 
                annotation_type,
                selected_classes,
                custom_model_path # <--- NOVO ARGUMENTO
            )
            
            # 2. Determina o tipo de anotação para guardar
            # (O SAM é um 'tipo' de modelo, mas produz 'segmentation')
            effective_annotation_type = annotation_type
            if annotation_type == 'sam':
                effective_annotation_type = 'segmentation'
            
            ia_service.create_annotations_from_results(
                db, 
                db_image=image, 
                results=results, 
                annotation_type=effective_annotation_type
            )
            
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

def export_annotations_labelme(db: Session, db_dataset: Dataset):
    """
    Gera um arquivo ZIP na memória com as anotações no formato LabelMe.
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for image in db_dataset.images:
            # 1. Obter dimensões da imagem
            try:
                with PILImage.open(image.file_path) as img:
                    img_width, img_height = img.size
            except FileNotFoundError:
                print(f"Arquivo de imagem não encontrado: {image.file_path}")
                continue # Pula esta imagem se o arquivo não for encontrado

            shapes = []
            for ann in image.annotations:
                shape = {
                    "label": ann.class_label,
                    "group_id": None,
                    "flags": {},
                }
                
                if ann.annotation_type == 'segmentation':
                    shape["shape_type"] = "polygon"
                    # Converte pontos normalizados [x, y] para pixels absolutos [x, y]
                    points = [[p[0] * img_width, p[1] * img_height] for p in ann.geometry]
                    shape["points"] = points
                else: # 'detection'
                    shape["shape_type"] = "rectangle"
                    # Converte [x_c, y_c, w, h] normalizados para [x_min, y_min], [x_max, y_max] em pixels
                    geo = ann.geometry
                    x_min = (geo['x'] - geo['width'] / 2) * img_width
                    y_min = (geo['y'] - geo['height'] / 2) * img_height
                    x_max = (geo['x'] + geo['width'] / 2) * img_width
                    y_max = (geo['y'] + geo['height'] / 2) * img_height
                    shape["points"] = [[x_min, y_min], [x_max, y_max]]
                
                shapes.append(shape)
            
            # 2. Montar a estrutura do JSON do LabelMe
            labelme_data = {
                "version": "3.18.0", # Versão que você especificou
                "flags": {},
                "shapes": shapes,
                "imagePath": image.file_name, # Caminho relativo
                "imageData": None, # Não vamos embutir a imagem
                "imageHeight": img_height,
                "imageWidth": img_width
            }
            
            # 3. Adicionar o arquivo JSON ao ZIP
            base_filename = os.path.splitext(image.file_name)[0]
            json_filename = f'{base_filename}.json'
            # Converte o dicionário Python para uma string JSON formatada
            zip_file.writestr(json_filename, json.dumps(labelme_data, indent=2))
    
    return zip_buffer.getvalue()

def _calculate_polygon_area(points):
    """Calcula a área de um polígono usando a fórmula de Shoelace."""
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

# --- NOVA FUNÇÃO DE EXPORTAÇÃO COCO ---
def export_annotations_coco(db: Session, db_dataset: Dataset):
    """
    Gera um arquivo ZIP na memória com as anotações no formato COCO (.json).
    """
    print("Iniciando exportação COCO...")
    
    # 1. Estrutura base do COCO
    coco_data = {
        "info": {
            "year": datetime.date.today().year,
            "version": "1.0",
            "description": f"Exportado de AdaptlabelX - Dataset: {db_dataset.name}",
        },
        "licenses": [{"id": 1, "name": "AdaptlabelX", "url": ""}],
        "categories": [],
        "images": [],
        "annotations": []
    }

    # 2. Criar mapa de categorias
    class_labels = sorted({ann.class_label for img in db_dataset.images for ann in img.annotations})
    class_map = {} # {'cat': 1, 'dog': 2}
    for i, label in enumerate(class_labels, 1): # IDs do COCO começam em 1
        coco_data["categories"].append({
            "id": i,
            "name": label,
            "supercategory": "all"
        })
        class_map[label] = i

    annotation_id_counter = 1
    image_id_counter = 1

    # 3. Processar cada imagem e suas anotações
    for image in db_dataset.images:
        try:
            with PILImage.open(image.file_path) as img:
                img_width, img_height = img.size
        except FileNotFoundError:
            print(f"Arquivo de imagem não encontrado: {image.file_path}")
            continue

        # Adicionar imagem à lista de imagens do COCO
        coco_image = {
            "id": image_id_counter,
            "file_name": image.file_name,
            "width": img_width,
            "height": img_height,
            "license": 1
        }
        coco_data["images"].append(coco_image)

        # Processar cada anotação desta imagem
        for ann in image.annotations:
            coco_ann = {
                "id": annotation_id_counter,
                "image_id": image_id_counter,
                "category_id": class_map[ann.class_label],
                "iscrowd": 0,
            }

            if ann.annotation_type == 'segmentation':
                # Converte [[x_n, y_n], ...] para [[x_abs, y_abs], ...]
                points_abs = [[p[0] * img_width, p[1] * img_height] for p in ann.geometry]
                
                # Converte para o formato COCO: [x1, y1, x2, y2, ...]
                coco_seg = [coord for point in points_abs for coord in point]
                
                # Calcula BBox a partir do polígono
                x_coords = [p[0] for p in points_abs]
                y_coords = [p[1] for p in points_abs]
                x_min = min(x_coords)
                y_min = min(y_coords)
                width = max(x_coords) - x_min
                height = max(y_coords) - y_min
                
                coco_ann["segmentation"] = [coco_seg]
                coco_ann["area"] = _calculate_polygon_area(points_abs)
                coco_ann["bbox"] = [x_min, y_min, width, height]

            else: # 'detection'
                geo = ann.geometry
                # Converte [x_c, y_c, w, h] normalizado para [x_min, y_min, w, h] absoluto
                width = geo['width'] * img_width
                height = geo['height'] * img_height
                x_min = (geo['x'] * img_width) - (width / 2)
                y_min = (geo['y'] * img_height) - (height / 2)
                
                coco_ann["bbox"] = [x_min, y_min, width, height]
                coco_ann["area"] = width * height
                # Opcional: criar segmentação a partir da bbox
                coco_ann["segmentation"] = [[x_min, y_min, x_min+width, y_min, x_min+width, y_min+height, x_min, y_min+height]]
            
            coco_data["annotations"].append(coco_ann)
            annotation_id_counter += 1
        
        image_id_counter += 1

    # 4. Preparar o arquivo ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        # Adiciona o único arquivo JSON ao ZIP
        json_content = json.dumps(coco_data, indent=2)
        zip_file.writestr('annotations.json', json_content)

    print("Exportação COCO concluída.")
    return zip_buffer.getvalue()

def export_annotations_cvat(db: Session, db_dataset: Dataset):
    """
    Gera um arquivo ZIP na memória com as anotações no formato CVAT XML.
    """
    print("Iniciando exportação CVAT...")
    
    # 1. Estrutura raiz do XML
    root = ET.Element('annotations')
    ET.SubElement(root, 'version').text = '1.1'
    
    # 2. Seção <meta>
    meta = ET.SubElement(root, 'meta')
    task = ET.SubElement(meta, 'task')
    ET.SubElement(task, 'name').text = db_dataset.name
    ET.SubElement(task, 'bugtracker')
    ET.SubElement(task, 'created').text = str(datetime.datetime.now())
    ET.SubElement(task, 'updated').text = str(datetime.datetime.now())
    
    # Adicionar labels (categorias) ao <meta>
    labels_element = ET.SubElement(task, 'labels')
    class_labels = sorted({ann.class_label for img in db_dataset.images for ann in img.annotations})
    for label_name in class_labels:
        label_element = ET.SubElement(labels_element, 'label')
        ET.SubElement(label_element, 'name').text = label_name
    
    # 3. Adicionar cada imagem e suas anotações
    for i, image in enumerate(db_dataset.images):
        try:
            with PILImage.open(image.file_path) as img:
                img_width, img_height = img.size
        except FileNotFoundError:
            continue

        image_element = ET.SubElement(root, 'image', id=str(i), name=image.file_name, 
                                      width=str(img_width), height=str(img_height))
        
        for ann in image.annotations:
            ann_attrs = {
                "label": ann.class_label,
                "occluded": "0",
            }
            
            if ann.annotation_type == 'segmentation':
                # Converte [[x_n, y_n], ...] para "x1,y1;x2,y2;..."
                points_list = []
                for p in ann.geometry:
                    x_abs = p[0] * img_width
                    y_abs = p[1] * img_height
                    points_list.append(f"{x_abs:.2f},{y_abs:.2f}")
                points_str = ";".join(points_list)
                ann_attrs["points"] = points_str
                ET.SubElement(image_element, 'polygon', ann_attrs)

            else: # 'detection'
                # Converte [x_c, y_c, w, h] normalizado para [xtl, ytl, xbr, ybr] absoluto
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
                
    # 4. Converter o XML para uma string formatada (pretty print)
    xml_str = ET.tostring(root, 'utf-8')
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    # 5. Preparar o arquivo ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr('annotations.xml', pretty_xml_str)

    print("Exportação CVAT concluída.")
    return zip_buffer.getvalue()