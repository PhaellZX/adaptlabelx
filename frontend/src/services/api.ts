import axios from 'axios';

const api = axios.create({
  baseURL: '/api', 
});

// Isso é chamado de "interceptor". Ele vai adicionar o token de autenticação
// em todas as requisições que fizermos para a API, se o token existir.
api.interceptors.request.use(async (config) => {
 const token = localStorage.getItem('@AdaptlabelX:token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;