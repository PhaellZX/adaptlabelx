// frontend/src/App.tsx
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { AppRoutes } from './routes';

function App() {
  return (
    // 1. O Router TEM de ser o "pai" de todos
    <Router>
      {/* 2. O AuthProvider TEM de estar DENTRO do Router */}
      <AuthProvider>
        {/* 3. As Rotas são o "neto", e agora podem usar o contexto E a navegação */}
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App;