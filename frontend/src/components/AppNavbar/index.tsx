// frontend/src/components/AppNavbar/index.tsx
import { Container, Button, Navbar, Nav } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export function AppNavbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/'); // Redireciona para a página de login após o logout
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
      <Container>
        <Navbar.Brand href="/dashboard">AdaptlabelX</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link href="/dashboard">Meus Datasets</Nav.Link>
            {/* ADICIONAMOS O LINK PARA A NOVA PÁGINA */}
            <Nav.Link href="/models">Meus Modelos</Nav.Link>
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
  );
}