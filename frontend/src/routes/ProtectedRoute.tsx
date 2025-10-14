import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { PropsWithChildren } from 'react';
import { Spinner } from 'react-bootstrap'; // Para um feedback visual

export function ProtectedRoute({ children }: PropsWithChildren) {
  const { isAuthenticated, isLoading } = useAuth();
  
   if (isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center vh-100">
        <Spinner animation="border" />
      </div>
    );
  }

  if (!isAuthenticated) {
    // Se o usuário não estiver autenticado, redireciona para a página de login
    return <Navigate to="/" replace />;
  }

  // Se estiver autenticado, renderiza o componente filho (a página protegida)
  return children;
}