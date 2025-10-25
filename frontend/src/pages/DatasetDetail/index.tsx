// frontend/src/pages/DatasetDetail/index.tsx

import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Button, Card, Row, Col, Form, Alert, Spinner } from 'react-bootstrap';
import api from '../../services/api';
import { AnnotationViewerModal } from '../../components/AnnotationViewerModal';
// --- 1. IMPORTAR OS TIPOS GLOBAIS ---
import { Image, Dataset } from '../../types'; 

// --- 2. AS DEFINIÇÕES LOCAIS DE 'Annotation', 'Image' e 'Dataset' FORAM REMOVIDAS ---

export function DatasetDetailPage() {
    const { datasetId } = useParams<{ datasetId: string }>();
    const [dataset, setDataset] = useState<Dataset | null>(null);
    const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [message, setMessage] = useState('');
    const [isAnnotating, setIsAnnotating] = useState(false);
    const [selectedImage, setSelectedImage] = useState<Image | null>(null);
    
    // --- 3. CORREÇÃO DO ERRO DA LINHA 41 ---
    const pollingRef = useRef<number | undefined>(undefined); // Dar um valor inicial
    const initialTotalAnnsRef = useRef<number>(0);
    const previousTotalAnnsRef = useRef<number>(0);
    const pollCountRef = useRef<number>(0);

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

        const initialTotal = dataset?.images.reduce((sum, img) => sum + img.annotations.length, 0) || 0;
        initialTotalAnnsRef.current = initialTotal;
        previousTotalAnnsRef.current = initialTotal;
        pollCountRef.current = 0;

        try {
            await api.post(`/datasets/${datasetId}/annotate`);
            pollingRef.current = window.setInterval(async () => {
                pollCountRef.current += 1;
                const updatedDataset = await fetchDataset();
                if (updatedDataset) {
                    const newTotal = updatedDataset.images.reduce((sum: number, img: Image) => sum + img.annotations.length, 0);
                    if (newTotal > previousTotalAnnsRef.current) {
                        previousTotalAnnsRef.current = newTotal;
                    } else if (newTotal === previousTotalAnnsRef.current && newTotal > initialTotalAnnsRef.current) {
                        clearInterval(pollingRef.current);
                        setIsAnnotating(false);
                        setMessage('Anotações concluídas com sucesso!');
                    } else if (pollCountRef.current > 5 && newTotal === initialTotalAnnsRef.current) {
                        clearInterval(pollingRef.current);
                        setIsAnnotating(false);
                        setMessage('Anotação concluída. Nenhuma nova anotação encontrada.');
                    } else if (pollCountRef.current > 120) {
                        clearInterval(pollingRef.current);
                        setIsAnnotating(false);
                        setMessage('Processo de anotação expirou.');
                    }
                }
            }, 5000);
        } catch (error) {
            console.error("Falha ao iniciar anotação:", error);
            setMessage('Erro ao iniciar o processo de anotação.');
            setIsAnnotating(false);
        }
    };

    // Função genérica para lidar com downloads de arquivos
    const handleDownload = async (url: string, defaultFilename: string) => {
        try {
            const response = await api.get(url, {
                responseType: 'blob',
            });
            const blobUrl = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = blobUrl;
            
            const contentDisposition = response.headers['content-disposition'];
            let filename = defaultFilename;
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
            console.error(`Falha ao baixar ${defaultFilename}:`, error);
            setMessage("Erro ao preparar o arquivo para download.");
        }
    };

    // Funções específicas de download
    const handleDownloadYolo = () => {
        handleDownload(`/datasets/${datasetId}/export/yolo`, `dataset_${datasetId}_yolo.zip`);
    };

    const handleDownloadLabelMe = () => {
        handleDownload(`/datasets/${datasetId}/export/labelme`, `dataset_${datasetId}_labelme.zip`);
    };
    
    const handleDownloadCoco = () => {
        handleDownload(`/datasets/${datasetId}/export/coco`, `dataset_${datasetId}_coco.zip`);
    };
    
    const handleDownloadCvat = () => {
        handleDownload(`/datasets/${datasetId}/export/cvat`, `dataset_${datasetId}_cvat.zip`);
    };

    // Funções para controlar o modal
    const handleImageClick = (image: Image) => setSelectedImage(image);
    const handleCloseModal = () => setSelectedImage(null);

    if (isLoading) {
        return (
            <div className="d-flex justify-content-center align-items-center vh-100">
                <Spinner animation="border" />
            </div>
        );
    }

    if (!dataset) return <p className="text-center mt-5">Dataset não encontrado.</p>;

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
                        <Card.Body className="d-flex flex-column align-items-center justify-content-center gap-2">
                            <Button variant="outline-primary" onClick={handleDownloadYolo} disabled={dataset.images.length === 0} className="w-100">
                               Baixar formato YOLO
                            </Button>
                            <Button variant="outline-secondary" onClick={handleDownloadLabelMe} disabled={dataset.images.length === 0} className="w-100">
                               Baixar formato LabelMe
                            </Button>
                            <Button variant="outline-info" onClick={handleDownloadCoco} disabled={dataset.images.length === 0} className="w-100">
                               Baixar formato COCO
                            </Button>
                            <Button variant="outline-dark" onClick={handleDownloadCvat} disabled={dataset.images.length === 0} className="w-100">
                               Baixar formato CVAT
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
                                <Card.Img 
                                    variant="top" 
                                    src={`http://127.0.0.1:8000/${image.file_path.replace(/\\/g, '/')}`} 
                                    alt={image.file_name}
                                    style={{ height: '200px', objectFit: 'cover' }}
                                />
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