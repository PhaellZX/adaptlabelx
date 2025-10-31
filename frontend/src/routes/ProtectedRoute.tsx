// frontend/src/routes/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Spinner, Container } from 'react-bootstrap'; // <--- 1. Importar o Container
import { ReactNode } from 'react';
import { AppNavbar } from '../components/AppNavbar';
import { Footer } from '../components/Footer';

export const ProtectedRoute = ({ children }: { children: ReactNode }) => {
  const { user, loading } = useAuth();

  if (loading) {
    // O seu 'loading' está perfeito, mostra o layout
    return (
      <>
        <AppNavbar />
        <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '80vh' }}>
          <Spinner animation="border" />
        </Container>
        <Footer />
      </>
    );
  }

  if (!user) {
    // Se não está a carregar e não há utilizador, redireciona
    return <Navigate to="/" replace />;
  }

  // --- 2. ESTA É A CORREÇÃO ---
  // Se não está a carregar E o 'user' existe, MOSTRA O LAYOUT
  // e "embrulha" os 'children' (a sua página)
  return (
    <>
      <AppNavbar />
      <Container as="main" className="py-4" style={{ minHeight: '80vh' }}>
        {children} {/* <-- Aqui é onde o DashboardPage/DatasetDetailPage/etc. aparecem */}
      </Container>
      <Footer />
    </>
  );
  // --- FIM DA CORREÇÃO ---
};