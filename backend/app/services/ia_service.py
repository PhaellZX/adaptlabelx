# backend/app/services/ia_service.py

from ultralytics import YOLO
from ultralytics.models.sam import SAM
from sqlalchemy.orm import Session
import io
import zipfile
import os
from typing import List, Optional, Dict, Any

from app.models.dataset import Image
from app.models.annotation import Annotation

# --- Cache para Modelos Customizados ---
# Isto evita recarregar o modelo .pt (que é lento) para cada imagem.
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
        # 1. Retorna o modelo do cache se já estiver carregado
        print(f"Carregando modelo customizado do cache: {model_path}")
        return custom_model_cache[model_path]
    
    # 2. Se não, carrega do disco e armazena em cache
    print(f"Carregando novo modelo customizado do disco: {model_path}")
    try:
        model = YOLO(model_path)
        custom_model_cache[model_path] = model
        return model
    except Exception as e:
        print(f"ERRO: Falha ao carregar modelo customizado {model_path}: {e}")
        # Limpa o cache se falhar
        if model_path in custom_model_cache:
            del custom_model_cache[model_path]
        return None

def run_model_on_image(
    image_path: str, 
    model_type: str, 
    selected_classes: Optional[List[str]] = None,
    custom_model_path: Optional[str] = None # <-- Argumento principal
):
    """
    Executa o modelo apropriado (padrão ou customizado) numa imagem.
    """
    
    model = None
    
    # --- 1. Determina qual modelo carregar ---
    if custom_model_path:
        model = _get_model(custom_model_path)
        if model is None:
            raise Exception(f"Não foi possível carregar o modelo customizado de {custom_model_path}")
    elif model_type == 'sam':
        # Pipeline SAM é especial, não usa a variável 'model' principal
        pass
    elif model_type == 'segmentation':
        model = segmentation_model
    else: # 'detection'
        model = detection_model

    # --- 2. Lógica de Filtro de Classes ---
    # Isto agora funciona para QUALQUER modelo carregado (padrão ou customizado)
    class_indices = []
    filter_args = {}
    
    # Determina o mapa de nomes correto (padrão, customizado, ou do detector para SAM)
    model_names_map = {}
    if model_type == 'sam' and not custom_model_path:
        model_names_map = detection_model.names # SAM usa o detector padrão
    elif model:
        model_names_map = model.names # Modelo customizado ou padrão YOLO
        
    if selected_classes and model_names_map:
        name_to_index_map = {v: k for k, v in model_names_map.items()}
        class_indices = [name_to_index_map[name] for name in selected_classes if name in name_to_index_map]
        print(f"Filtrando por classes: {selected_classes} (Índices: {class_indices})")
        filter_args = {"classes": class_indices}

    # --- 3. Executa o pipeline de anotação ---
    if model_type == 'sam' and not custom_model_path:
        # Pipeline SAM (usa o 'detection_model' com filtros)
        print(f"Rodando pipeline SAM para: {image_path}")
        det_results_list = detection_model(image_path, verbose=False, **filter_args)
        det_results = det_results_list[0]
        
        if len(det_results.boxes) == 0:
            print("Nenhum objeto detectado pelo YOLO, pulando SAM.")
            return det_results
        
        sam_results_list = sam_model(image_path, bboxes=det_results.boxes.xyxy, verbose=False)
        sam_results = sam_results_list[0]
        
        if sam_results.masks:
            sam_results.names = det_results.names 
            sam_results.boxes = det_results.boxes
        
        return sam_results
    
    elif model:
        # Pipeline Padrão (Detecção/Segmentação) ou Customizado
        return model(image_path, verbose=False, **filter_args)[0]
    
    else:
        raise Exception("Nenhum modelo válido foi determinado para anotação.")


def create_annotations_from_results(db: Session, db_image: Image, results, annotation_type: str):
    """
    Processa os resultados do modelo e cria os registros de anotação no banco.
    (Esta função não precisa de mudanças, já é genérica)
    """
    new_annotations = []
    class_names = results.names
    
    if annotation_type == 'segmentation':
        if results.masks is None: 
            print("Resultados de segmentação não contêm máscaras.")
            return []
            
        for i, mask in enumerate(results.masks):
            class_id = int(results.boxes[i].cls[0])
            confidence = float(results.boxes[i].conf[0])
            polygon = mask.xyn[0].tolist()
            
            db_annotation = Annotation(
                annotation_type='segmentation', 
                class_label=class_names[class_id],
                confidence=confidence,
                geometry=polygon,
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
    
    if new_annotations:
        db.commit()
        for ann in new_annotations: 
            db.refresh(ann)
            
    return new_annotations