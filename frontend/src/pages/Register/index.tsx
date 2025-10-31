// frontend/src/pages/Register/index.tsx

import { useState } from 'react';
import { Container, Form, Button, Alert, Card } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../services/api';

export function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('As senhas não coincidem.');
      return;
    }

    try {
      await api.post('/users/', {
        email: email,
        password: password,
      });
      navigate('/'); 
    } catch (err: any) {
      console.error("Falha no cadastro:", err);
      setError(err.response?.data?.detail || 'Falha no cadastro. Tente outro email.');
    }
  };

  return (
    // --- A MUDANÇA ESTÁ AQUI ---
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
            <h2 className="mb-0">Cadastro</h2>
          </div>

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
            <Form.Group className="mb-3">
              <Form.Label>Confirmar Senha</Form.Label>
              <Form.Control
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </Form.Group>
            <Button variant="primary" type="submit" className="w-100">
              Cadastrar
            </Button>
          </Form>
          <div className="mt-3 text-center">
            Já tem uma conta? <Link to="/">Faça login</Link>
          </div>
        </Card.Body>
      </Card>
    </Container>
  );
}