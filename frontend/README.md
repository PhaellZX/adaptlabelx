# ⚛️ Frontend (React App) - AdaptLabelX

Esta pasta contém a aplicação React (SPA) para a plataforma AdaptLabelX.

## 🛠️ Stack Tecnológica

* **React 18:** Para a construção da interface de usuário.
* **TypeScript:** Para tipagem estática.
* **React Router DOM:** Para gerenciamento de rotas.
* **React-Bootstrap:** Para componentes de UI (Modais, Cards, Navbar).
* **Axios:** Para fazer requisições à API do backend.
* **Nginx:** Para servir os ficheiros estáticos e atuar como proxy reverso.

## 📂 Estrutura de Pastas
```
frontend/ 
├── public/ 
├── src/ 
│ ├── components/ # Componentes reutilizáveis (AppNavbar, Footer, Modais)
│ ├── contexts/ # Contexto de Autenticação (AuthContext) 
│ ├── pages/ # Páginas principais (Login, Dashboard, DatasetDetail) 
│ ├── routes/ # Configuração das Rotas (index.tsx, ProtectedRoute.tsx) 
│ ├── services/ # Configuração do Axios (api.ts)
│ ├── types/ # Definições de tipos (index.ts) 
│ ├── App.tsx # Componente raiz
│ └── main.tsx # Ponto de entrada do React
├── Dockerfile 
└── nginx.conf # Configuração do Proxy Nginx
```

## ⚙️ Configuração do Proxy (Nginx)

Este frontend **não** precisa de um ficheiro `.env` para a URL da API, pois o Nginx trata de toda a comunicação. O `nginx.conf` está configurado para:

1.  Servir a aplicação React como um SPA (Single Page Application).
2.  Redirecionar todos os pedidos de API para o backend.
3.  Redirecionar todos os pedidos de imagens (uploads) para o backend.
```
# frontend/nginx.conf

# Proxy da API
location /api/ {
    proxy_pass http://backend:8000/; 
}

# Proxy de Imagens
location /uploads/ {
    proxy_pass http://backend:8000/uploads/;
}
```

## 🚀 Como Executar

Este serviço é projetado para ser executado com o Docker Compose a partir da raiz do projeto.

1. Construir e Subir os Contêineres:
```
docker-compose up --build
```

2. A aplicação estará disponível em: http://localhost