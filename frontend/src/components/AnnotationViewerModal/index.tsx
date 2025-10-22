import { useEffect, useRef } from 'react';
import { Modal, Button } from 'react-bootstrap';

// --- Tipagem dos Dados ---

// Tipagem flexível para a geometria
type Geometry = {
    x: number;
    y: number;
    width: number;
    height: number;
} | [number, number][]; // Pode ser um objeto (bbox) ou um array de pontos (polígono)

// Tipagem para a anotação
interface Annotation {
    class_label: string;
    confidence: number;
    annotation_type: string; // 'detection' or 'segmentation'
    geometry: Geometry;
}

// Tipagem para a imagem
interface Image {
    file_path: string;
    annotations: Annotation[];
}

// Tipagem para as props do componente
interface AnnotationViewerModalProps {
    show: boolean;
    handleClose: () => void;
    image: Image | null;
}

export function AnnotationViewerModal({ show, handleClose, image }: AnnotationViewerModalProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        // Só executa se o modal estiver visível, tiver uma imagem e o canvas estiver pronto
        if (show && image && canvasRef.current) {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');

            if (ctx) {
                const img = new window.Image();
                // Monta a URL completa para o backend
                img.src = `http://127.0.0.1:8000/${image.file_path}`;
                
                // Define o que acontece quando a imagem terminar de carregar
                img.onload = () => {
                    // Ajusta o tamanho do canvas para o tamanho real da imagem
                    canvas.width = img.width;
                    canvas.height = img.height;

                    // 1. Desenha a imagem de fundo no canvas
                    ctx.drawImage(img, 0, 0);

                    // 2. Itera sobre as anotações para desenhar
                    image.annotations.forEach(ann => {
                        // Define estilos de fonte e cor
                        const color = ann.annotation_type === 'segmentation' ? 'rgba(0, 255, 0, 0.8)' : 'red';
                        ctx.strokeStyle = color;
                        ctx.fillStyle = color;
                        ctx.lineWidth = 2;
                        ctx.font = '14px Arial';

                        const label = `${ann.class_label} (${(ann.confidence * 100).toFixed(1)}%)`;
                        let labelX = 0;
                        let labelY = 0;

                        if (ann.annotation_type === 'segmentation') {
                            // --- LÓGICA PARA DESENHAR POLÍGONOS ---
                            const polygon = ann.geometry as [number, number][];
                            if (polygon.length === 0) return;

                            ctx.beginPath();
                            // Move para o primeiro ponto
                            const startPoint = polygon[0];
                            labelX = startPoint[0] * img.width;
                            labelY = startPoint[1] * img.height;
                            ctx.moveTo(labelX, labelY);

                            // Desenha linhas para os pontos restantes
                            for (let i = 1; i < polygon.length; i++) {
                                ctx.lineTo(polygon[i][0] * img.width, polygon[i][1] * img.height);
                            }
                            ctx.closePath(); // Fecha o polígono

                            ctx.fillStyle = 'rgba(0, 255, 0, 0.3)'; // Preenchimento verde semi-transparente
                            ctx.stroke();
                            ctx.fill();

                        } else {
                            // --- LÓGICA PARA DESENHAR CAIXAS (BOUNDING BOX) ---
                            const geometry = ann.geometry as { x: number; y: number; width: number; height: number };
                            const { x, y, width, height } = geometry;
                            
                            // Converte coordenadas normalizadas [centro_x, centro_y, w, h] para pixels [topo_x, topo_y, w, h]
                            const rectWidth = width * img.width;
                            const rectHeight = height * img.height;
                            const rectX = (x * img.width) - (rectWidth / 2);
                            const rectY = (y * img.height) - (rectHeight / 2);

                            // Desenha o retângulo
                            ctx.strokeRect(rectX, rectY, rectWidth, rectHeight);
                            
                            labelX = rectX;
                            labelY = rectY;
                        }

                        // Desenha o rótulo da classe
                        ctx.fillStyle = color; // Reseta o fillStyle para o texto
                        ctx.fillText(label, labelX, labelY > 10 ? labelY - 5 : 10);
                    });
                };
            }
        }
    }, [show, image]); // O efeito roda sempre que o modal abre ou a imagem muda

    return (
        <Modal show={show} onHide={handleClose} size="lg" centered>
            <Modal.Header closeButton>
                <Modal.Title>Visualizador de Anotações</Modal.Title>
            </Modal.Header>
            <Modal.Body className="text-center" style={{ maxHeight: '80vh', overflowY: 'auto' }}>
                {/* O canvas onde tudo será desenhado */}
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