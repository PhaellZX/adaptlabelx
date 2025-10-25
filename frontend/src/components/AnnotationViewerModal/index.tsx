// frontend/src/components/AnnotationViewerModal/index.tsx

import { useEffect, useRef } from 'react';
import { Modal, Button } from 'react-bootstrap';

// --- 1. Importar os tipos centrais ---
import { Image, BoundingBox, Polygon } from '../../types';

// --- 2. As definições de tipo locais foram REMOVIDAS daqui ---

// --- 3. Atualizar as Props para usar o tipo importado ---
interface AnnotationViewerModalProps {
    show: boolean;
    handleClose: () => void;
    image: Image | null;
}

export function AnnotationViewerModal({ show, handleClose, image }: AnnotationViewerModalProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        if (show && image && canvasRef.current) {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');

            if (ctx) {
                const img = new window.Image();
                
                // --- 4. Usar a porta correta (8000) e o replace() ---
                img.src = `http://127.0.0.1:8000/${image.file_path.replace(/\\/g, '/')}`;
                
                img.onload = () => {
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);

                    image.annotations.forEach(ann => {
                        const color = ann.annotation_type === 'segmentation' ? 'rgba(0, 255, 0, 0.8)' : 'red';
                        ctx.strokeStyle = color;
                        ctx.fillStyle = color;
                        ctx.lineWidth = 2;
                        ctx.font = '14px Arial';

                        const label = `${ann.class_label} (${(ann.confidence * 100).toFixed(1)}%)`;
                        let labelX = 0;
                        let labelY = 0;

                        // --- 5. Usar os tipos importados para "casting" ---
                        if (ann.annotation_type === 'segmentation') {
                            const polygon = ann.geometry as Polygon; // Usar o tipo Polygon importado
                            if (polygon.length === 0) return;
                            
                            ctx.beginPath();
                            const startPoint = polygon[0];
                            labelX = startPoint[0] * img.width;
                            labelY = startPoint[1] * img.height;
                            ctx.moveTo(labelX, labelY);
                            
                            for (let i = 1; i < polygon.length; i++) {
                                ctx.lineTo(polygon[i][0] * img.width, polygon[i][1] * img.height);
                            }
                            
                            ctx.closePath();
                            ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
                            ctx.stroke();
                            ctx.fill();

                        } else { // 'detection'
                            const geometry = ann.geometry as BoundingBox; // Usar o tipo BoundingBox importado
                            const { x, y, width, height } = geometry;
                            const rectWidth = width * img.width;
                            const rectHeight = height * img.height;
                            const rectX = (x * img.width) - (rectWidth / 2);
                            const rectY = (y * img.height) - (rectHeight / 2);
                            
                            ctx.strokeRect(rectX, rectY, rectWidth, rectHeight);
                            labelX = rectX;
                            labelY = rectY;
                        }
                        
                        ctx.fillStyle = color;
                        ctx.fillText(label, labelX, labelY > 10 ? labelY - 5 : 10);
                    });
                };
            }
        }
    }, [show, image]);

    return (
        <Modal show={show} onHide={handleClose} size="lg" centered>
            <Modal.Header closeButton>
                <Modal.Title>Visualizador de Anotações</Modal.Title>
            </Modal.Header>
            <Modal.Body className="text-center" style={{ maxHeight: '80vh', overflowY: 'auto' }}>
                <canvas 
                    ref={canvasRef} 
                    style={{ maxWidth: '100%', height: 'auto' }} 
                />
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>
                    Fechar
                </Button>
            </Modal.Footer>
        </Modal>
    );
}