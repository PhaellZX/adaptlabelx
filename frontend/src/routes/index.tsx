// frontend/src/routes/index.tsx
import { Routes, Route } from 'react-router-dom';
import { LoginPage } from '../pages/Login';
import { RegisterPage } from '../pages/Register';
import { DashboardPage } from '../pages/Dashboard';
import { ProtectedRoute } from './ProtectedRoute'; // O seu ficheiro (enviado) chama-se 'PrivateRoute.tsx'
                                                // Vou usar o nome 'ProtectedRoute' que está no seu import
import { DatasetDetailPage } from '../pages/DatasetDetail'; 

// --- 1. IMPORTAR A NOVA PÁGINA ---
// (Nós vamos criar esta página no próximo passo)
import { CustomModelsPage } from '../pages/CustomModels';

export function AppRoutes() {
  return (
    <Routes>
      {/* Rotas Públicas */}
      <Route path="/" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      {/* Rotas Protegidas */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/datasets/:datasetId" 
        element={
          <ProtectedRoute>
            <DatasetDetailPage />
          </ProtectedRoute>
        } 
      />
      
      {/* --- 2. ADICIONAR A NOVA ROTA DE MODELOS --- */}
      <Route 
        path="/models" 
        element={
          <ProtectedRoute>
            <CustomModelsPage />
          </ProtectedRoute>
        } 
      />
      {/* --- FIM DA NOVA ROTA --- */}
      
    </Routes>
  );
}