import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', 
});

// Isso é chamado de "interceptor". Ele vai adicionar o token de autenticação
// em todas as requisições que fizermos para a API, se o token existir.
api.interceptors.request.use(async (config) => {
  const token = localStorage.getItem('adaptlabel_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;