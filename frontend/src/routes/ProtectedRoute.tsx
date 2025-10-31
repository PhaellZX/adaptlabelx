import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Spinner, Container } from 'react-bootstrap'; 
import { ReactNode } from 'react';
import { AppNavbar } from '../components/AppNavbar';
import { Footer } from '../components/Footer';

export const ProtectedRoute = ({ children }: { children: ReactNode }) => {
  const { user, loading } = useAuth();

  if (loading) {
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

  return (
    <>
      <AppNavbar />
      <Container as="main" className="py-4" style={{ minHeight: '80vh' }}>
        {children} {/* <-- Aqui é onde o DashboardPage/DatasetDetailPage/etc. aparecem */}
      </Container>
      <Footer />
    </>
  );
};