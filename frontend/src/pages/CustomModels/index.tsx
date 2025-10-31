import { useState, useEffect } from 'react';
import { Container, Button, Form, Card, Row, Col, Alert, ListGroup, Spinner } from 'react-bootstrap';
import api from '../../services/api'; 

// Tipagem para o modelo customizado
interface CustomModel {
  id: number;
  name: string;
  model_type: string;
  file_path: string;
}

export function CustomModelsPage() {
  const [models, setModels] = useState<CustomModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [message, setMessage] = useState('');

  // States para o formulário de upload
  const [name, setName] = useState('');
  const [modelType, setModelType] = useState('detection');
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  // Função para buscar os modelos
  const fetchModels = async () => {
    try {
      const response = await api.get('/custom-models/');
      setModels(response.data);
    } catch (error) {
      console.error("Falha ao buscar modelos", error);
      setMessage('Falha ao carregar lista de modelos.');
    } finally {
      setIsLoading(false);
    }
  };

  // Buscar modelos ao carregar a página
  useEffect(() => {
    fetchModels();
  }, []);

  // Handler para o upload
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setMessage('Por favor, selecione um arquivo .pt');
      return;
    }

    setIsUploading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('name', name);
    formData.append('model_type', modelType);
    formData.append('file', file);

    try {
      await api.post('/custom-models/', formData);
      setMessage('Upload realizado com sucesso!');
      // Limpar formulário e recarregar lista
      setName('');
      setModelType('detection');
      setFile(null);
      fetchModels(); 
    } catch (error: any) {
      console.error("Falha no upload", error);
      setMessage(error.response?.data?.detail || 'Erro no upload.');
    } finally {
      setIsUploading(false);
    }
  };

  // Handler para deletar
  const handleDelete = async (modelId: number) => {
    if (window.confirm('Tem certeza que deseja excluir este modelo?')) {
      try {
        await api.delete(`/custom-models/${modelId}`);
        setMessage('Modelo excluído com sucesso.');
        fetchModels(); // Recarrega a lista
      } catch (error) {
        console.error("Falha ao excluir", error);
        setMessage('Falha ao excluir o modelo.');
      }
    }
  };

  return (
    <>
      <Container>
        {message && <Alert variant={message.includes('sucesso') ? 'success' : 'danger'}>{message}</Alert>}
        
        <Row>
          {/* Coluna da Lista de Modelos */}
          <Col md={7}>
            <h2>Meus Modelos</h2>
            {isLoading ? (
              <Spinner animation="border" />
            ) : (
              <ListGroup>
                {models.length > 0 ? models.map(model => (
                  <ListGroup.Item key={model.id} className="d-flex justify-content-between align-items-center">
                    <div>
                      <strong>{model.name}</strong>
                      <small className="d-block text-muted">Tipo: {model.model_type}</small>
                    </div>
                    <Button variant="outline-danger" size="sm" onClick={() => handleDelete(model.id)}>
                      Excluir
                    </Button>
                  </ListGroup.Item>
                )) : <p>Você ainda não fez upload de nenhum modelo.</p>}
              </ListGroup>
            )}
          </Col>

          {/* Coluna do Formulário de Upload */}
          <Col md={5}>
            <Card>
              <Card.Header>Fazer Upload de Novo Modelo</Card.Header>
              <Card.Body>
                <Form onSubmit={handleUpload}>
                  <Form.Group className="mb-3">
                    <Form.Label>Nome do Modelo</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="Ex: Meu Modelo de Gatos"
                      value={name}
                      onChange={e => setName(e.target.value)}
                      required
                    />
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Tipo de Modelo</Form.Label>
                    <Form.Select value={modelType} onChange={e => setModelType(e.target.value)}>
                      <option value="detection">Detecção (Caixas)</option>
                      <option value="segmentation">Segmentação (Polígonos)</option>
                    </Form.Select>
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Arquivo do Modelo (.pt)</Form.Label>
                    <Form.Control
                      type="file"
                      accept=".pt"
                      onChange={e => setFile((e.target as HTMLInputElement).files?.[0] || null)}
                      required
                    />
                  </Form.Group>
                  <Button variant="primary" type="submit" disabled={isUploading}>
                    {isUploading ? <Spinner as="span" size="sm" /> : 'Enviar'}
                  </Button>
                </Form>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </>
  );
}