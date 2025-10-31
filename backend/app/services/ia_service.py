from ultralytics import YOLO
from ultralytics.models.sam import SAM
from sqlalchemy.orm import Session
import io
import zipfile
import os
from typing import List, Optional, Dict, Any

from app.models.dataset import Image
from app.models.annotation import Annotation
from app.services import custom_model_service
from app.core.database import SessionLocal

# --- Cache para Modelos Customizados ---
custom_model_cache: Dict[str, Any] = {}

# --- Modelos Padrão ---
MODEL_DIR = "ia_models"
detection_model = YOLO(os.path.join(MODEL_DIR, 'yolov8n.pt'))
segmentation_model = YOLO(os.path.join(MODEL_DIR, 'yolov8n-seg.pt'))
sam_model = SAM(os.path.join(MODEL_DIR, 'sam_b.pt'))

def _get_model(model_path: str):
    """
    Função auxiliar para carregar e fazer cache de modelos customizados.
    """
    if model_path in custom_model_cache:
        print(f"Carregando modelo customizado do cache: {model_path}")
        return custom_model_cache[model_path]
    
    print(f"Carregando modelo customizado do disco: {model_path}")
    if not os.path.exists(model_path):
        print(f"Erro: Modelo customizado não encontrado em {model_path}")
        return None
        
    model = YOLO(model_path)
    custom_model_cache[model_path] = model
    return model

def run_model_on_image(
    image_path: str, 
    model_type: str, # Recebe 'yolov8n_det', 'sam', ou um ID '1'
    selected_classes: Optional[List[str]] = None,
    owner_id: Optional[int] = None
):
    """
    Carrega o modelo correto e executa-o com o filtro de classes.
    """
    model = None
    model_names_map = None
    filter_args = {}
    is_standard_model = False

    # 1. Determinar qual modelo carregar
    if model_type == "yolov8n_det":
        model = detection_model
        model_names_map = model.names
        is_standard_model = True
    elif model_type == "yolov8n_seg":
        model = segmentation_model
        model_names_map = model.names
        is_standard_model = True
    elif model_type == "sam":
        model = sam_model
        model_names_map = detection_model.names 
        is_standard_model = True
    else:
        # Lógica para Modelo Customizado (ex: model_type='1')
        if owner_id is None:
            print("Erro: owner_id é necessário para carregar um modelo customizado.")
            return None
        try:
            db_temp = SessionLocal()
            
            custom_model = custom_model_service.get_model(
                db_temp, 
                model_id=int(model_type), 
                owner_id=owner_id
            )
            db_temp.close()
            
            if custom_model:
                model = _get_model(custom_model.file_path) # Carrega o .pt
                if model:
                    model_names_map = model.names
            else:
                 print(f"Erro: Modelo customizado com ID {model_type} não encontrado para o dono {owner_id}.")
                 return None
        except Exception as e:
            print(f"Erro ao carregar modelo customizado {model_type}: {e}")
            return None

    if model is None:
        print(f"Não foi possível carregar o modelo para {model_type}")
        return None
    
    if selected_classes and model_names_map and is_standard_model:
        class_indices = [
            k for k, v in model_names_map.items() if v in selected_classes
        ]
        if class_indices:
            print(f"Filtrando por classes: {selected_classes} (Índices: {class_indices})")
            filter_args = {"classes": class_indices}
        else:
            print(f"Aviso: Classes {selected_classes} não encontradas no modelo.")
    elif not is_standard_model:
        print("Modelo customizado detectado. A anotar com todas as classes do modelo.")
        filter_args = {}

    # 4. Executar o pipeline de anotação
    if model_type == 'sam':
        print("Executando pipeline SAM (YOLOv8 -> SAM)...")
        det_results_list = detection_model(image_path, verbose=False, **filter_args)
        if not det_results_list or not det_results_list[0].boxes:
             print("SAM: Nenhum objeto de 'prompt' (YOLO) encontrado.")
             return None
        sam_results = sam_model.predict(image_path, bboxes=det_results_list[0].boxes.xyxy)
        if sam_results and sam_results[0].masks:
            sam_results[0].boxes = det_results_list[0].boxes 
        return sam_results[0]
        
    elif model:
        print(f"Executando modelo {model_type}...")
        return model(image_path, verbose=False, **filter_args)[0]
    
    return None


def create_annotations_from_results(
    db: Session, 
    results: Any, 
    db_image: Image, 
    model_id: str, # 'yolov8n_det', 'sam', ou '1'
    owner_id: Optional[int] = None
):
    """
    Salva as anotações na base de dados.
    """
    if results is None:
        print(f"Nenhum resultado para salvar para a imagem {db_image.file_name}")
        return []
        
    new_annotations = []
    class_names = None
    annotation_type = ""

    # 1. Determinar o mapa de classes (class_names)
    if model_id == "yolov8n_det":
        class_names = detection_model.names
        annotation_type = "detection"
    elif model_id == "yolov8n_seg":
        class_names = segmentation_model.names
        annotation_type = "segmentation"
    elif model_id == "sam":
        class_names = detection_model.names
        annotation_type = "segmentation"
    else:
        # Lógica para Modelo Customizado
        if owner_id is None:
            print("Erro: owner_id é necessário para salvar resultados de modelo customizado.")
            return []
        try:
            db_temp = SessionLocal()

            custom_model = custom_model_service.get_model(
                db_temp, 
                model_id=int(model_id), 
                owner_id=owner_id
            )
            db_temp.close()
            if custom_model:
                model = _get_model(custom_model.file_path)
                if model:
                    class_names = model.names
                annotation_type = custom_model.model_type # 'detection' ou 'segmentation'
        except Exception as e:
            print(f"Não foi possível carregar 'names' para o modelo customizado {model_id}: {e}")

    if class_names is None or not annotation_type:
        print(f"Erro: Não foi possível determinar 'class_names' ou 'annotation_type' para o model_id {model_id}")
        return []

    # 2. Salvar as anotações com base no tipo
    if annotation_type == 'segmentation':
        if results.masks is None or results.boxes is None:
            print(f"Modelo {model_id} não produziu máscaras ou caixas.")
            return []
            
        for i, mask in enumerate(results.masks):
            if i >= len(results.boxes): continue 
            class_id = int(results.boxes[i].cls[0])
            if class_id not in class_names:
                print(f"Erro: class_id {class_id} não encontrado no mapa de classes.")
                continue
            
            db_annotation = Annotation(
                annotation_type='segmentation', 
                class_label=class_names[class_id],
                confidence=float(results.boxes[i].conf[0]),
                geometry=mask.xyn[0].tolist(),
                image_id=db_image.id
            )
            db.add(db_annotation)
            new_annotations.append(db_annotation)

    elif annotation_type == 'detection': 
        if results.boxes is None:
            print("Resultados de detecção não contêm caixas.")
            return []

        for box in results.boxes:
            class_id = int(box.cls[0])
            if class_id not in class_names:
                print(f"Erro: class_id {class_id} não encontrado no mapa de classes.")
                continue
            
            x, y, w, h = box.xywhn[0]
            geometry_data = {"x": float(x), "y": float(y), "width": float(w), "height": float(h)}
            
            db_annotation = Annotation(
                annotation_type='detection',
                class_label=class_names[class_id],
                confidence=float(box.conf[0]),
                geometry=geometry_data,
                image_id=db_image.id
            )
            db.add(db_annotation)
            new_annotations.append(db_annotation)
            
    print(f"Salvas {len(new_annotations)} novas anotações para a imagem {db_image.file_name}.")
    return new_annotations