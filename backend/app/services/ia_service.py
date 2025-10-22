# backend/app/services/ia_service.py
from ultralytics import YOLO
from sqlalchemy.orm import Session

from app.models.dataset import Image
from app.models.annotation import Annotation
from app.schemas.annotation import AnnotationCreate

# Carrega os dois modelos que vamos usar
detection_model = YOLO('yolov8n.pt')
segmentation_model = YOLO('yolov8n-seg.pt') # Modelo de segmentação

def run_model_on_image(image_path: str, model_type: str):
    """Executa o modelo YOLO apropriado em uma imagem."""
    if model_type == 'segmentation':
        model = segmentation_model
    else:
        model = detection_model
    results = model(image_path, verbose=False)
    return results[0]

def create_annotations_from_results(db: Session, db_image: Image, results, annotation_type: str):
    """Processa os resultados e cria as anotações."""
    new_annotations = []
    class_names = results.names

    if annotation_type == 'segmentation':
        # Lógica para processar máscaras de segmentação
        if results.masks is None: return [] # Pula se não houver máscaras
        for i, mask in enumerate(results.masks):
            class_id = int(results.boxes[i].cls[0])
            confidence = float(results.boxes[i].conf[0])
            
            # Converte a máscara para um polígono normalizado
            polygon = mask.xyn[0].tolist() # Lista de pontos [x, y]
            
            db_annotation = Annotation(
                annotation_type='segmentation',
                class_label=class_names[class_id],
                confidence=confidence,
                geometry=polygon, # Salva a lista de pontos
                image_id=db_image.id
            )
            db.add(db_annotation)
            new_annotations.append(db_annotation)

    else: # Lógica para detecção (bounding boxes), como já tínhamos
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
    
    db.commit()
    for ann in new_annotations: db.refresh(ann)
    return new_annotations