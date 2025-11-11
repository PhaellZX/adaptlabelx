import { useState, useEffect } from 'react';
import { Container, Form, Button, Alert, Card } from 'react-bootstrap';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const { login } = useAuth();
  const location = useLocation(); // <--- 4. Obter a "location"
  const navigate = useNavigate(); // <--- 5. Obter o "navigate"

  useEffect(() => {
    // Verifica se a página foi carregada com uma mensagem de estado
    if (location.state?.message) {
      setSuccessMessage(location.state.message);
      
      // Limpa o estado da localização para que a mensagem
      // não apareça novamente se o usuário atualizar a página (F5)
      navigate('.', { replace: true, state: {} });
    }
  }, [location.state, navigate]); // Depende de location.state

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccessMessage(null);

    try {
      const success = await login(email, password);
      if (!success) {
        setError('Falha no login. Verifique seu email e senha.');
      }
    } catch (err) {
      console.error(err);
      setError('Falha no login. Verifique seu email e senha.');
    }
  };

  return (
    <Container fluid className="d-flex align-items-center justify-content-center bg-light h-100 animation-fade-in-up">
      <Card className="shadow-lg border-0" style={{ width: '400px' }}>
        <Card.Body className="p-4 p-md-5">
          <div className="text-center mb-4">
            <img
              src="/logo.png"
              alt="AdaptlabelX Logo"
              className="d-block mx-auto mb-3" 
              style={{ width: '200px' }}
            />
            <h2 className="mb-0">Login</h2>
          </div>
          {/* --- Mostrar o Alerta de Erro OU Sucesso --- */}
          {error && <Alert variant="danger">{error}</Alert>}
          {successMessage && <Alert variant="success">{successMessage}</Alert>}
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Endereço de Email</Form.Label>
              <Form.Control
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Senha</Form.Label>
              <Form.Control
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </Form.Group>
            <Button variant="primary" type="submit" className="w-100">
              Entrar
            </Button>
          </Form>
          <div className="mt-3 text-center">
            Não tem uma conta? <Link to="/register">Cadastre-se</Link>
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
}