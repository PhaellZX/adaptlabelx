// frontend/src/pages/Dashboard/index.tsx

import { useState, useEffect } from 'react';
import { Container, Button, Card, Row, Col, Spinner, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom'; // O import continua correto
import api from '../../services/api';
import { CreateDatasetModal } from '../../components/CreateDatasetModal';
// Importe o seu tipo de Dataset (se o tiver num ficheiro central)
import { Dataset } from '../../types'; 

export function DashboardPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);

  const fetchDatasets = async () => {
    try {
      setIsLoading(true);
      const response = await api.get('/datasets/');
      setDatasets(response.data);
      setError('');
    } catch (err) {
      console.error("Falha ao buscar datasets:", err);
      setError('Não foi possível carregar os seus datasets.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleDelete = async (datasetId: number) => {
    if (window.confirm('Tem a certeza que quer excluir este dataset? Todas as imagens e anotações serão perdidas permanentemente.')) {
      try {
        await api.delete(`/datasets/${datasetId}`);
        setDatasets(datasets.filter(dataset => dataset.id !== datasetId));
      } catch (err) {
        console.error("Falha ao excluir o dataset:", err);
        setError('Não foi possível excluir o dataset. Tente novamente.');
      }
    }
  };

  const handleModalClose = () => setShowModal(false);
  const handleDatasetCreated = (newDataset: Dataset) => {
    setDatasets([...datasets, newDataset]);
  };

  if (isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: 'calc(100vh - 200px)' }}>
        <Spinner animation="border" />
      </div>
    );
  }

  return (
    <>
      <Container className="mt-4">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2>Meus Datasets</h2>
          <Button variant="primary" onClick={() => setShowModal(true)}>
            Criar Novo Dataset
          </Button>
        </div>

        {error && <Alert variant="danger">{error}</Alert>}

        <Row>
          {datasets.length > 0 ? (
            datasets.map(dataset => (
              <Col md={4} key={dataset.id} className="mb-4">
                <Card className="h-100 shadow-sm">
                  <Card.Body className="d-flex flex-column">
                    <Card.Title>{dataset.name}</Card.Title>
                    <Card.Text className="text-muted flex-grow-1">
                      {dataset.description || 'Sem descrição.'}
                    </Card.Text>
                    
                    {/* --- ESTA É A CORREÇÃO (LINHA 99) --- */}
                    <div className="d-flex justify-content-end gap-2 mt-3">
                      
                      {/* 1. O Link "embrulha" o Botão.
                          'role="button"' é importante para a acessibilidade.
                          'text-decoration-none' remove o sublinhado do link.
                      */}
                      <Link to={`/datasets/${dataset.id}`} role="button" className="text-decoration-none">
                        <Button 
                          variant="primary"
                          size="sm"
                          className="w-100" // Faz o botão preencher o link
                        >
                          Entrar
                        </Button>
                      </Link>
                      
                      <Button 
                        onClick={() => handleDelete(dataset.id)} 
                        variant="outline-danger"
                        size="sm"
                      >
                        Excluir
                      </Button>
                    </div>
                    {/* --- FIM DA CORREÇÃO --- */}
                    
                  </Card.Body>
                </Card>
              </Col>
            ))
          ) : (
            <Col>
              {!isLoading && (
                <Alert variant="info">
                  Você ainda não criou nenhum dataset. Clique em "Criar Novo Dataset" para começar!
                </Alert>
              )}
            </Col>
          )}
        </Row>
      </Container>

      <CreateDatasetModal
        show={showModal}
        handleClose={handleModalClose}
        onDatasetCreated={handleDatasetCreated}
      />
    </>
  );
}