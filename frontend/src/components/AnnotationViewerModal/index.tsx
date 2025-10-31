import { useEffect, useRef } from 'react';
import { Modal, Button } from 'react-bootstrap';

// Importar os tipos centrais
import { Image, BoundingBox, Polygon } from '../../types';

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
                
                img.src = `/uploads/${image.file_path.replace(/\\/g, '/')}`;
                
                img.onload = () => {
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);

                    // Desenha as anotações
                    image.annotations.forEach(ann => {
                        const color = ann.annotation_type === 'segmentation' ? 'rgba(0, 255, 0, 0.8)' : 'red';
                        ctx.strokeStyle = color;
                        ctx.fillStyle = color;
                        ctx.lineWidth = 2;
                        ctx.font = '14px Arial';

                        const label = `${ann.class_label} (${(ann.confidence * 100).toFixed(1)}%)`;
                        let labelX = 0;
                        let labelY = 0;

                        if (ann.annotation_type === 'segmentation') {
                            const polygon = ann.geometry as Polygon; 
                            if (!polygon || polygon.length === 0) return;
                            
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
                            const geometry = ann.geometry as BoundingBox;
                            const { x, y, width, height } = geometry;
                            // Converte de [centro_x, centro_y, w, h] (normalizado) para [x_min, y_min, w, h] (pixels)
                            const rectWidth = width * img.width;
                            const rectHeight = height * img.height;
                            const rectX = (x * img.width) - (rectWidth / 2);
                            const rectY = (y * img.height) - (rectHeight / 2);
                            
                            ctx.strokeRect(rectX, rectY, rectWidth, rectHeight);
                            labelX = rectX;
                            labelY = rectY;
                        }
                        
                        // Desenha o rótulo (label)
                        ctx.fillStyle = color; // Restaura a cor sólida para o texto
                        ctx.fillText(label, labelX, labelY > 10 ? labelY - 5 : 10);
                    });
                };

                img.onerror = () => {
                    console.error("Falha ao carregar a imagem:", img.src);
                    if (ctx) {
                        ctx.fillStyle = "red";
                        ctx.font = "16px Arial";
                        ctx.fillText("Erro ao carregar imagem", 10, 50);
                    }
                }
            }
        }
    }, [show, image]); // O 'useEffect' corre sempre que a imagem ou 'show' mudam

    return (
        <Modal show={show} onHide={handleClose} size="lg" centered>
            <Modal.Header closeButton>
                <Modal.Title>{image ? image.file_name : 'Visualizador de Anotações'}</Modal.Title>
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