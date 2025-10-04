# backend/app/services/ia_service.py
from ultralytics import YOLO
from sqlalchemy.orm import Session

from app.models.dataset import Image
from app.models.annotation import Annotation
from app.schemas.annotation import AnnotationCreate

# Carrega o modelo YOLOv8n (um modelo pequeno e rápido, pré-treinado)
# O download será feito automaticamente na primeira vez que for executado.
model = YOLO('yolov8n.pt')

def run_model_on_image(image_path: str):
    """Executa o modelo YOLO em um único caminho de imagem."""
    results = model(image_path, verbose=False)  # verbose=False para um output mais limpo
    return results[0] # Retorna o resultado para a primeira (e única) imagem

def create_annotations_from_results(db: Session, db_image: Image, results):
    """
    Processa os resultados do modelo e cria os registros de anotação no banco.
    """
    new_annotations = []
    boxes = results.boxes
    class_names = results.names

    for box in boxes:
        # Extrai as informações da caixa delimitadora (bounding box)
        class_id = int(box.cls[0])
        class_label = class_names[class_id]
        confidence = float(box.conf[0])
        
        # Coordenadas no formato [x_centro, y_centro, largura, altura] normalizadas
        x, y, w, h = box.xywhn[0]
        
        geometry_data = {
            "x": float(x),
            "y": float(y),
            "width": float(w),
            "height": float(h)
        }
        
        annotation_in = AnnotationCreate(
            class_label=class_label,
            confidence=confidence,
            geometry=geometry_data
        )
        
        db_annotation = Annotation(
            **annotation_in.model_dump(),
            image_id=db_image.id
        )
        db.add(db_annotation)
        new_annotations.append(db_annotation)
        
    db.commit()
    for ann in new_annotations:
        db.refresh(ann)
        
    return new_annotations