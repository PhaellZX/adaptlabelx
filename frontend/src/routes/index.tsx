// frontend/src/routes/index.tsx
import { Routes, Route } from 'react-router-dom';
// NÃO importe o Router ou AuthProvider aqui
import { LoginPage } from '../pages/Login';
import { RegisterPage } from '../pages/Register';
import { DashboardPage } from '../pages/Dashboard';
import { ProtectedRoute } from './ProtectedRoute';
import { DatasetDetailPage } from '../pages/DatasetDetail'; 
import { CustomModelsPage } from '../pages/CustomModels';

export function AppRoutes() {
  return (
    // O <Router> e <AuthProvider> já estão no App.tsx
    <Routes> 
      <Route path="/" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/datasets/:datasetId" element={<ProtectedRoute><DatasetDetailPage /></ProtectedRoute>} />
      <Route path="/models" element={<ProtectedRoute><CustomModelsPage /></ProtectedRoute>} />
    </Routes>
  );
}