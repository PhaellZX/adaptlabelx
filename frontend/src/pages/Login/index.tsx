// frontend/src/pages/Login/index.tsx

import { useState } from 'react';
import { Container, Form, Button, Alert, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext'; // 1. Importar o useAuth

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth(); // 2. Obter a função de login do contexto

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      // 3. Chamar a função de login do AuthContext
      const success = await login(email, password);

      if (!success) {
        setError('Falha no login. Verifique seu email e senha.');
      }
      // Se 'success' for true, o AuthContext irá tratar do redirecionamento
    } catch (err) {
      console.error(err);
      setError('Falha no login. Verifique seu email e senha.');
    }
  };

  return (
    <Container className="d-flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
      <Card style={{ width: '400px' }}>
        <Card.Body>
          <h2 className="text-center mb-4">Login</h2>
          {error && <Alert variant="danger">{error}</Alert>}
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