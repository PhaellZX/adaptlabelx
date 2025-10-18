// frontend/src/components/AnnotationViewerModal/index.tsx

import { useEffect, useRef } from 'react';
import { Modal, Button } from 'react-bootstrap';

// Reutilizando as tipagens que já temos
interface Annotation {
    class_label: string;
    confidence: number;
    geometry: {
        x: number;
        y: number;
        width: number;
        height: number;
    };
}

interface Image {
    file_path: string;
    annotations: Annotation[];
}

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
                img.src = `http://127.0.0.1:8000/${image.file_path}`;
                img.onload = () => {
                    // Ajusta o tamanho do canvas para o tamanho da imagem
                    canvas.width = img.width;
                    canvas.height = img.height;

                    // 1. Desenha a imagem no canvas
                    ctx.drawImage(img, 0, 0);

                    // 2. Itera sobre as anotações para desenhar as caixas
                    image.annotations.forEach(ann => {
                        const { x, y, width, height } = ann.geometry;

                        // Converte as coordenadas normalizadas (0-1) para pixels
                        const rectX = (x - width / 2) * img.width;
                        const rectY = (y - height / 2) * img.height;
                        const rectWidth = width * img.width;
                        const rectHeight = height * img.height;

                        // Configura o estilo do desenho
                        ctx.strokeStyle = 'red'; // Cor da caixa
                        ctx.lineWidth = 2;
                        ctx.fillStyle = 'red';
                        ctx.font = '14px Arial';

                        // Desenha o retângulo (bounding box)
                        ctx.strokeRect(rectX, rectY, rectWidth, rectHeight);

                        // Escreve o rótulo da classe e a confiança
                        const label = `${ann.class_label} (${(ann.confidence * 100).toFixed(1)}%)`;
                        ctx.fillText(label, rectX, rectY > 10 ? rectY - 5 : 10);
                    });
                };
            }
        }
    }, [show, image]); // O efeito roda sempre que o modal abre ou a imagem muda

    return (
        <Modal show={show} onHide={handleClose} size="lg">
            <Modal.Header closeButton>
                <Modal.Title>Visualizador de Anotações</Modal.Title>
            </Modal.Header>
            <Modal.Body className="text-center">
                {/* O canvas onde tudo será desenhado */}
                <canvas ref={canvasRef} style={{ maxWidth: '100%', height: 'auto' }} />
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>
                    Fechar
                </Button>
            </Modal.Footer>
        </Modal>
    );
}