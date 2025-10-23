// frontend/src/pages/Dashboard/index.tsx

import { useState, useEffect } from 'react';
import { Container, Button, Card, Row, Col } from 'react-bootstrap';
// Note que 'Navbar' e 'Nav' não são mais necessários aqui
import { Link } from 'react-router-dom'; 
import api from '../../services/api';
import { AppNavbar } from '../../components/AppNavbar'; // 1. Importar o Navbar separado
import { CreateDatasetModal } from '../../components/CreateDatasetModal';

// Tipagem para um dataset
interface Dataset {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  images: any[];
}

export function DashboardPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [showModal, setShowModal] = useState(false);

  // Função reutilizável para buscar os datasets do usuário
  const fetchDatasets = async () => {
    try {
      const response = await api.get('/datasets/');
      setDatasets(response.data);
    } catch (error) {
      console.error("Falha ao buscar datasets:", error);
    }
  };

  // Efeito que busca os datasets quando a página carrega
  useEffect(() => {
    fetchDatasets();
  }, []); // O array vazio [] garante que isso rode apenas uma vez

  // Função chamada pelo Modal após a criação de um dataset
  const handleDatasetCreated = (success: boolean) => {
    if (success) {
      fetchDatasets(); // Força a atualização da lista
    }
  };

  // Função para deletar um dataset
  const handleDelete = async (datasetId: number) => {
    if (window.confirm('Tem certeza que deseja excluir este dataset?')) {
      try {
        await api.delete(`/datasets/${datasetId}`);
        // Remove o dataset da lista localmente
        setDatasets(prevDatasets => prevDatasets.filter(d => d.id !== datasetId));
      } catch (error) {
        console.error("Falha ao deletar dataset:", error);
        alert("Erro ao deletar o dataset.");
      }
    }
  };

  return (
    <>
      {/* 2. Usar o componente AppNavbar */}
      <AppNavbar /> 

      {/* 3. Container não precisa mais do 'mt-4' (está no AppNavbar) */}
      <Container>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1>Meus Datasets</h1>
          <Button variant="primary" onClick={() => setShowModal(true)}>
            Criar Novo Dataset
          </Button>
        </div>
        
        <Row>
          {datasets.length > 0 ? (
            datasets.map((dataset) => (
              <Col md={4} key={dataset.id} className="mb-3">
                <Link to={`/datasets/${dataset.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                  <Card className="h-100 shadow-sm">
                    <Card.Body>
                      <Card.Title>{dataset.name || "Dataset sem nome"}</Card.Title>
                      <Card.Text>{dataset.description || 'Sem descrição.'}</Card.Text>
                    </Card.Body>
                  </Card>
                </Link>
                <Card.Footer>
                   <Button variant="outline-danger" size="sm" onClick={() => handleDelete(dataset.id)}>
                       Excluir
                   </Button>
                </Card.Footer>
              </Col>
            ))
          ) : (
            <p>Você ainda não tem nenhum dataset. Crie um para começar!</p>
          )}
        </Row>
      </Container>

      <CreateDatasetModal 
        show={showModal}
        handleClose={() => setShowModal(false)}
        onDatasetCreated={handleDatasetCreated}
      />
    </>
  );
}