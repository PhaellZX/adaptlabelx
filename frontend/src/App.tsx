// frontend/src/App.tsx
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { AppRoutes } from './routes';
import './App.css'; // O CSS ainda é global

function App() {
  return (
    // Apenas Provedores e Rotas. NENHUM layout (divs, main, footer) aqui.
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;