import { createContext, useState, useContext, useEffect, PropsWithChildren } from 'react';
import api from '../services/api';

// Tipagem para os dados do usuário e do contexto
interface User {
  id: number;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
}

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true); // NOVO: Inicia carregando

  // Carrega o token e os dados do usuário do localStorage ao iniciar
  useEffect(() => {
    const token = localStorage.getItem('adaptlabel_token');
    const userData = localStorage.getItem('adaptlabel_user');
    if (token && userData) {
      setUser(JSON.parse(userData));
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    setIsLoading(false); 
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', new URLSearchParams({
      username: email,
      password: password,
    }));
    const { access_token } = response.data;
    
    localStorage.setItem('adaptlabel_token', access_token);
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

    const userResponse = await api.get('/users/me');
    setUser(userResponse.data);
    localStorage.setItem('adaptlabel_user', JSON.stringify(userResponse.data));
  };

  const register = async (email: string, password: string) => {
    await api.post('/users/', { email, password });
    await login(email, password);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('adaptlabel_token');
    localStorage.removeItem('adaptlabel_user');
    delete api.defaults.headers.common['Authorization'];
  };
  
  return (
    <AuthContext.Provider value={{ isAuthenticated: !!user, isLoading, user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook customizado para facilitar o uso do contexto
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}