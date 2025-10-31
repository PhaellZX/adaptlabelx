import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Função auxiliar para configurar o token
const setAuthorizationHeader = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Efeito para carregar o utilizador no arranque
  useEffect(() => {
    const token = localStorage.getItem('@AdaptlabelX:token');
    if (token) {
      setAuthorizationHeader(token);
      api.get('/users/me')
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          // Token inválido, limpar
          localStorage.removeItem('@AdaptlabelX:token');
          setAuthorizationHeader(null);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await api.post('/auth/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });

      const { access_token } = response.data;

      // 1. Guardar o token
      localStorage.setItem('@AdaptlabelX:token', access_token);
      // 2. Configurar o token para pedidos futuros
      setAuthorizationHeader(access_token);

      const userResponse = await api.get('/users/me', {
        headers: {
          Authorization: `Bearer ${access_token}`
        }
      });
      
      setUser(userResponse.data);
      setLoading(false);
      navigate('/dashboard');
      return true;

    } catch (error) {
      console.error("Erro no login:", error);
      setLoading(false);
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('@AdaptlabelX:token');
    setAuthorizationHeader(null);
    navigate('/');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};