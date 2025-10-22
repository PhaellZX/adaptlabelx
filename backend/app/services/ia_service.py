# backend/app/services/ia_service.py

from ultralytics import YOLO
from ultralytics.models.sam import SAM
from sqlalchemy.orm import Session
import io
import zipfile
import os
from typing import List, Optional # Importar List e Optional

from app.models.dataset import Image
from app.models.annotation import Annotation

# Carrega todos os modelos que vamos usar
# Estes arquivos serão baixados pelo ultralytics na primeira execução
detection_model = YOLO('yolov8n.pt')
segmentation_model = YOLO('yolov8n-seg.pt')
sam_model = SAM('sam_b.pt')

def run_model_on_image(
    image_path: str, 
    model_type: str, 
    selected_classes: Optional[List[str]] = None # Argumento para filtrar classes
):
    """
    Executa o modelo YOLO apropriado em uma imagem, filtrando por classes.
    """
    
    model = None
    
    if model_type == 'segmentation':
        model = segmentation_model
    elif model_type == 'sam':
        # Para o SAM, o filtro é aplicado no primeiro estágio (detecção)
        model = detection_model 
    else: # 'detection'
        model = detection_model

    # --- Lógica de conversão e filtro ---
    class_indices = []
    if selected_classes:
        # Inverte o mapa de nomes do modelo (ex: {0: 'person'} -> {'person': 0})
        name_to_index_map = {v: k for k, v in model.names.items()}
        # Converte a lista de nomes (ex: ['cat', 'dog']) para índices (ex: [15, 16])
        class_indices = [name_to_index_map[name] for name in selected_classes if name in name_to_index_map]
        print(f"Filtrando por classes: {selected_classes} (Índices: {class_indices})")
    
    # O argumento 'classes' filtra os resultados para nós
    # Se a lista estiver vazia, nenhum filtro é aplicado
    filter_args = {"classes": class_indices} if class_indices else {}
    
    # --- Execução dos modelos (atualizada) ---
    if model_type == 'sam':
        print(f"Rodando pipeline SAM para: {image_path}")
        # 1. Detectar objetos com YOLO (com filtro)
        det_results_list = detection_model(image_path, verbose=False, **filter_args)
        det_results = det_results_list[0]
        
        if len(det_results.boxes) == 0:
            print("Nenhum objeto detectado pelo YOLO, pulando SAM.")
            return det_results # Retorna resultado vazio
        
        # 2. Usar as caixas do YOLO como prompts para o SAM
        sam_results_list = sam_model(image_path, bboxes=det_results.boxes.xyxy, verbose=False)
        sam_results = sam_results_list[0]
        
        # 3. CRÍTICO: Copiar o objeto 'Boxes' inteiro do YOLO para o SAM
        if sam_results.masks:
            sam_results.names = det_results.names 
            sam_results.boxes = det_results.boxes # Transfere 'cls' e 'conf'
        
        return sam_results # Retorna o objeto de resultado com máscaras do SAM e classes do YOLO
    
    else:
        # Para 'detection' e 'segmentation', o filtro é aplicado diretamente
        return model(image_path, verbose=False, **filter_args)[0]

def create_annotations_from_results(db: Session, db_image: Image, results, annotation_type: str):
    """
    Processa os resultados do modelo e cria os registros de anotação no banco.
    """
    new_annotations = []
    class_names = results.names
    
    # Unificamos a lógica de 'segmentation' e 'sam', pois ambas geram máscaras/polígonos
    if (annotation_type == 'segmentation' or annotation_type == 'sam'):
        if results.masks is None: 
            print("Resultados de segmentação não contêm máscaras.")
            return []
            
        for i, mask in enumerate(results.masks):
            # Esta parte agora funcionará, pois results.boxes tem 'cls' e 'conf'
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