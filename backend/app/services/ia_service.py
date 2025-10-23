# backend/app/services/ia_service.py

from ultralytics import YOLO
from ultralytics.models.sam import SAM
from sqlalchemy.orm import Session
import io
import zipfile
import os # Importar o 'os' para construir caminhos
from typing import List, Optional

from app.models.dataset import Image
from app.models.annotation import Annotation

# --- 1. Definir o caminho para a nova pasta ---
# (Assume que o script é executado da raiz do 'backend')
MODEL_DIR = "ia_models"

# --- 2. Atualizar os caminhos para carregar os modelos ---
detection_model = YOLO(os.path.join(MODEL_DIR, 'yolov8n.pt'))
segmentation_model = YOLO(os.path.join(MODEL_DIR, 'yolov8n-seg.pt'))
sam_model = SAM(os.path.join(MODEL_DIR, 'sam_b.pt'))


def run_model_on_image(
    image_path: str, 
    model_type: str, 
    selected_classes: Optional[List[str]] = None
):
    """
    Executa o modelo YOLO apropriado em uma imagem, filtrando por classes.
    """
    
    model = None
    
    if model_type == 'segmentation':
        model = segmentation_model
    elif model_type == 'sam':
        model = detection_model 
    else: # 'detection'
        model = detection_model

    class_indices = []
    if selected_classes:
        name_to_index_map = {v: k for k, v in model.names.items()}
        class_indices = [name_to_index_map[name] for name in selected_classes if name in name_to_index_map]
        print(f"Filtrando por classes: {selected_classes} (Índices: {class_indices})")
    
    filter_args = {"classes": class_indices} if class_indices else {}
    
    if model_type == 'sam':
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
    
    else:
        return model(image_path, verbose=False, **filter_args)[0]

def create_annotations_from_results(db: Session, db_image: Image, results, annotation_type: str):
    """
    Processa os resultados do modelo e cria os registros de anotação no banco.
    """
    new_annotations = []
    class_names = results.names
    
    if (annotation_type == 'segmentation' or annotation_type == 'sam'):
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