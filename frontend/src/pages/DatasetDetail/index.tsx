import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Button, Card, Row, Col, Form, Alert, Spinner } from 'react-bootstrap';
import api from '../../services/api';

// --- Tipagem dos Dados ---
interface Annotation {
    id: number;
    class_label: string;
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
    const pollingRef = useRef<number>(); // Referência para o intervalo de polling

    // Função reutilizável para buscar os dados do dataset
    const fetchDataset = async () => {
        try {
            const response = await api.get(`/datasets/${datasetId}`);
            setDataset(response.data);
            return response.data; // Retorna os dados para uso no polling
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

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelectedFiles(event.target.files);
    };

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
            setSelectedFiles(null); // Limpa a seleção de arquivos
        } catch (error) {
            console.error("Falha no upload:", error);
            setMessage('Erro no upload. Tente novamente.');
        }
    };

    const handleAnnotate = async () => {
        setIsAnnotating(true);
        setMessage('Iniciando anotação em segundo plano... Isso pode levar alguns minutos.');
        try {
            await api.post(`/datasets/${datasetId}/annotate`);

            // Inicia o polling para verificar o status
            pollingRef.current = window.setInterval(async () => {
                const updatedDataset = await fetchDataset();
                if (updatedDataset && updatedDataset.images.length > 0) {
                    // Condição de parada: verifica se TODAS as imagens têm pelo menos uma anotação.
                    const allAnnotated = updatedDataset.images.every((img: Image) => img.annotations.length > 0);
                    if (allAnnotated) {
                        clearInterval(pollingRef.current);
                        setIsAnnotating(false);
                        setMessage('Anotações concluídas com sucesso!');
                    }
                }
            }, 5000); // Verifica a cada 5 segundos

        } catch (error) {
            console.error("Falha ao iniciar anotação:", error);
            setMessage('Erro ao iniciar o processo de anotação.');
            setIsAnnotating(false);
        }
    };

    if (isLoading) {
        return (
            <div className="d-flex justify-content-center align-items-center vh-100">
                <Spinner animation="border" />
            </div>
        );
    }

    if (!dataset) return <p className="text-center mt-5">Dataset não encontrado.</p>;

    return (
        <Container className="mt-4">
            <Link to="/dashboard">{"< Voltar para o Dashboard"}</Link>
            <h1 className="mt-2">{dataset.name}</h1>
            <p>{dataset.description}</p>

            <hr />

            <Card className="mb-4">
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
                        <Card>
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
    );
}
