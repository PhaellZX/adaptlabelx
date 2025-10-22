// frontend/src/pages/DatasetDetail/index.tsx

import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Button, Card, Row, Col, Form, Alert, Spinner } from 'react-bootstrap';
import api from '../../services/api';
import { AnnotationViewerModal } from '../../components/AnnotationViewerModal';

// --- Tipagem dos Dados (Completa) ---
interface Annotation {
    id: number;
    class_label: string;
    confidence: number;
    geometry: any; // Flexível para bbox ou polígono
}

interface Image {
    id: number;
    file_name: string;
    file_path: string;
    annotations: Annotation[];
}

interface Dataset {
    id: number;
    name: string;
    description: string;
    images: Image[];
}

export function DatasetDetailPage() {
    const { datasetId } = useParams<{ datasetId: string }>();
    const [dataset, setDataset] = useState<Dataset | null>(null);
    const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [message, setMessage] = useState('');
    const [isAnnotating, setIsAnnotating] = useState(false);
    const [selectedImage, setSelectedImage] = useState<Image | null>(null);
    
    // --- Refs para a lógica de polling ---
    const pollingRef = useRef<number>();
    const initialTotalAnnsRef = useRef<number>(0);
    const previousTotalAnnsRef = useRef<number>(0);
    const pollCountRef = useRef<number>(0); // Para evitar loops infinitos

    // Função reutilizável para buscar os dados do dataset
    const fetchDataset = async () => {
        try {
            const response = await api.get(`/datasets/${datasetId}`);
            setDataset(response.data);
            return response.data;
        } catch (error) {
            console.error("Falha ao buscar o dataset:", error);
            setMessage('Erro ao carregar os dados do dataset.');
            return null;
        }
    };

    // Efeito para buscar os dados iniciais e limpar o polling ao sair da página
    useEffect(() => {
        fetchDataset().finally(() => setIsLoading(false));
        return () => clearInterval(pollingRef.current);
    }, [datasetId]);

    // Função para lidar com a seleção de arquivos
    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelectedFiles(event.target.files);
    };

    // Função para fazer o upload dos arquivos
    const handleUpload = async () => {
        if (!selectedFiles) return;
        const formData = new FormData();
        for (let i = 0; i < selectedFiles.length; i++) {
            formData.append("files", selectedFiles[i]);
        }
        try {
            const response = await api.post(`/datasets/${datasetId}/images/`, formData);
            setDataset(prev => prev ? { ...prev, images: [...prev.images, ...response.data] } : null);
            setMessage('Upload realizado com sucesso!');
            setSelectedFiles(null);
        } catch (error) {
            console.error("Falha no upload:", error);
            setMessage('Erro no upload. Tente novamente.');
        }
    };

    // Função para iniciar a anotação automática
    const handleAnnotate = async () => {
        setIsAnnotating(true);
        setMessage('Iniciando anotação em segundo plano... Isso pode levar alguns minutos.');

        // Salva o estado inicial
        const initialTotal = dataset?.images.reduce((sum, img) => sum + img.annotations.length, 0) || 0;
        initialTotalAnnsRef.current = initialTotal;
        previousTotalAnnsRef.current = initialTotal;
        pollCountRef.current = 0;

        try {
            await api.post(`/datasets/${datasetId}/annotate`);

            // Inicia o polling
            pollingRef.current = window.setInterval(async () => {
                pollCountRef.current += 1;
                const updatedDataset = await fetchDataset();

                if (updatedDataset) {
                    const newTotal = updatedDataset.images.reduce((sum: number, img: Image) => sum + img.annotations.length, 0);

                    // A NOVA LÓGICA DE PARADA
                    if (newTotal > previousTotalAnnsRef.current) {
                        // Progresso foi feito. Atualiza o contador e continua.
                        previousTotalAnnsRef.current = newTotal;
                    } else if (newTotal === previousTotalAnnsRef.current && newTotal > initialTotalAnnsRef.current) {
                        // O total é o mesmo do poll anterior E é maior que o inicial.
                        // Significa que o processo terminou.
                        clearInterval(pollingRef.current);
                        setIsAnnotating(false);
                        setMessage('Anotações concluídas com sucesso!');
                    } else if (pollCountRef.current > 5 && newTotal === initialTotalAnnsRef.current) {
                        // Se por 25s (5 polls) nada mudou, paramos também (caso o modelo não encontre nada)
                        clearInterval(pollingRef.current);
                        setIsAnnotating(false);
                        setMessage('Anotação concluída. Nenhuma nova anotação encontrada.');
                    } else if (pollCountRef.current > 120) { // Timeout de 10 min
                        clearInterval(pollingRef.current);
                        setIsAnnotating(false);
                        setMessage('Processo de anotação expirou.');
                    }
                }
            }, 5000); // Verifica a cada 5 segundos

        } catch (error) {
            console.error("Falha ao iniciar anotação:", error);
            setMessage('Erro ao iniciar o processo de anotação.');
            setIsAnnotating(false);
        }
    };

    // Função para baixar as anotações
    const handleDownloadYolo = async () => {
        try {
            const response = await api.get(`/datasets/${datasetId}/export/yolo`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            const contentDisposition = response.headers['content-disposition'];
            let filename = `dataset_${datasetId}_yolo.zip`;
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                if (filenameMatch && filenameMatch.length === 2)
                    filename = filenameMatch[1];
            }
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode?.removeChild(link);
        } catch (error) {
            console.error("Falha ao baixar as anotações:", error);
            setMessage("Erro ao preparar o arquivo para download.");
        }
    };

    // Funções para controlar o modal
    const handleImageClick = (image: Image) => setSelectedImage(image);
    const handleCloseModal = () => setSelectedImage(null);

    // Renderização de loading
    if (isLoading) {
        return (
            <div className="d-flex justify-content-center align-items-center vh-100">
                <Spinner animation="border" />
            </div>
        );
    }

    // Renderização de dataset não encontrado
    if (!dataset) return <p className="text-center mt-5">Dataset não encontrado.</p>;

    // Renderização da página
    return (
        <>
            <Container className="mt-4">
                <Link to="/dashboard">{"< Voltar para o Dashboard"}</Link>
                <h1 className="mt-2">{dataset.name}</h1>
                <p>{dataset.description}</p>
                <hr />

                <div className="d-flex flex-wrap gap-3 mb-4">
                    <Card className="flex-grow-1" style={{minWidth: '300px'}}>
                        <Card.Header>Fazer Upload de Novas Imagens</Card.Header>
                        <Card.Body>
                            <Form.Group>
                                <Form.Control type="file" multiple onChange={handleFileChange} />
                            </Form.Group>
                            <Button className="mt-3" onClick={handleUpload} disabled={!selectedFiles}>
                                Enviar Imagens
                            </Button>
                        </Card.Body>
                    </Card>
                    <Card style={{minWidth: '250px'}}>
                        <Card.Header>Exportar Anotações</Card.Header>
                        <Card.Body className="d-flex align-items-center justify-content-center">
                            <Button variant="outline-primary" onClick={handleDownloadYolo} disabled={dataset.images.length === 0}>
                               Baixar formato YOLO
                            </Button>
                        </Card.Body>
                    </Card>
                </div>

                <div className="d-flex justify-content-between align-items-center mb-4">
                    <h2>Imagens do Dataset ({dataset.images.length})</h2>
                    <Button variant="success" onClick={handleAnnotate} disabled={isAnnotating || dataset.images.length === 0}>
                        {isAnnotating && <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" />}
                        {isAnnotating ? ' Anotando...' : 'Anotar Automaticamente'}
                    </Button>
                </div>

                {message && <Alert variant="info">{message}</Alert>}

                <Row>
                    {dataset.images.map(image => (
                        <Col md={3} key={image.id} className="mb-3">
                            <Card onClick={() => handleImageClick(image)} style={{ cursor: 'pointer' }}>
                                <Card.Img variant="top" src={`http://127.0.0.1:8000/${image.file_path}`} />
                                <Card.Body>
                                    <Card.Text className="text-truncate">{image.file_name}</Card.Text>
                                    <Card.Text><strong>Anotações:</strong> {image.annotations.length}</Card.Text>
                                </Card.Body>
                            </Card>
                        </Col>
                    ))}
                </Row>
            </Container>
            
            <AnnotationViewerModal
                show={!!selectedImage}
                handleClose={handleCloseModal}
                image={selectedImage}
            />
        </>
    );
}