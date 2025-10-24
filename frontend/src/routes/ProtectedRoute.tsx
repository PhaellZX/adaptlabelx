// frontend/src/routes/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Spinner } from 'react-bootstrap';
import { ReactNode } from 'react'; // <--- 1. Importar o ReactNode

export const ProtectedRoute = ({ children }: { children: ReactNode }) => { // <--- 2. Esta é a correção
  const { user, loading } = useAuth();

  if (loading) {
    // Se o AuthContext está 'loading' (a verificar o token
    // ou a processar o login), esperamos.
    return (
      <div className="d-flex justify-content-center align-items-center vh-100">
        <Spinner animation="border" />
      </div>
    );
  }

  if (!user) {
    // Se NÃO está a carregar E o 'user' é 'null',
    // então o utilizador não está mesmo logado. Redireciona.
    return <Navigate to="/" replace />;
  }

  // Se NÃO está a carregar E 'user' existe, mostra a página.
  return children;
};