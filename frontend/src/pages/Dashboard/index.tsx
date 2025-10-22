// frontend/src/pages/Dashboard/index.tsx

import { useState, useEffect } from 'react';
import { Container, Button, Navbar, Nav, Card, Row, Col } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom'; // Importar o Link
import api from '../../services/api';
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
  const { user, logout } = useAuth();
  const navigate = useNavigate();
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
      fetchDatasets(); // Força a atualização da lista, corrigindo o bug
    }
  };

  // Função de logout
  const handleLogout = () => {
    logout();
    navigate('/');
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
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand href="/dashboard">AdaptlabelX</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link href="/dashboard">Meus Datasets</Nav.Link>
            </Nav>
            <Nav>
              <Navbar.Text className="me-3">
                Logado como: {user?.email}
              </Navbar.Text>
              <Button variant="outline-light" onClick={handleLogout}>
                Sair
              </Button>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container className="mt-4">
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
                {/* Link envolve o Card para torná-lo clicável */}
                <Link to={`/datasets/${dataset.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                  <Card className="h-100 shadow-sm">
                    <Card.Body>
                      <Card.Title>{dataset.name || "Dataset sem nome"}</Card.Title>
                      <Card.Text>{dataset.description || 'Sem descrição.'}</Card.Text>
                    </Card.Body>
                  </Card>
                </Link>
                {/* Botão de excluir fica fora do Link, no Footer */}
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

      {/* Renderiza o Modal de Criação */}
      <CreateDatasetModal 
        show={showModal}
        handleClose={() => setShowModal(false)}
        onDatasetCreated={handleDatasetCreated}
      />
    </>
  );
}