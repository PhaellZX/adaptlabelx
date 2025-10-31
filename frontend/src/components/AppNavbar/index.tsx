// frontend/src/components/AppNavbar/index.tsx
import { Container, Button, Navbar, Nav } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom'; // 1. Importar o Link

export function AppNavbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    // O AuthContext já deve tratar do redirecionamento,
    // mas podemos garantir aqui.
    navigate('/');
  };

  return (
    // 2. Adicionada uma sombra (shadow-sm)
    <Navbar bg="dark" variant="dark" expand="lg" className="mb-4 shadow-sm">
      <Container>
        {/* --- 3. GRANDE MUDANÇA AQUI --- */}
        {/* Usar 'as={Link}' e 'to' para navegação SPA */}
        <Navbar.Brand as={Link} to="/dashboard">
          <img
            src="/logo.png" // Busca o logo.png na pasta /public
            width="30"
            height="30"
            className="d-inline-block align-top me-2"
            alt="AdaptlabelX Logo"
          />
          <strong>AdaptLabelX</strong>
        </Navbar.Brand>
        {/* --- Fim da Mudança --- */}

        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          {/* 4. Usar 'as={Link}' nos links também */}
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/dashboard">Meus Datasets</Nav.Link>
            <Nav.Link as={Link} to="/models">Meus Modelos</Nav.Link>
          </Nav>
          <Nav>
            {user && (
              <Navbar.Text className="me-3">
                Logado como: {user.email}
              </Navbar.Text>
            )}
            <Button variant="outline-light" onClick={handleLogout}>
              Sair
            </Button>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}