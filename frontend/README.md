# ⚛️ Frontend (React App) - AdaptLabelX

This folder contains the React application (SPA) for the AdaptLabelX platform.

## 🛠️ Technology Stack

* **React 18:** For building the user interface.
* **TypeScript:** For static typing.
* **React Router DOM:** For route management.
* **React-Bootstrap:** For UI components (Modals, Cards, Navbar).
* **Axios:** For making requests to the backend API.
* **Nginx:** For serving static files and acting as a reverse proxy.

## 📂 Folder Structure
```
frontend/
├── public/
├── src/
│ ├── components/ # Reusable components (AppNavbar, Footer, Modals)
│ ├── contexts/ # Authentication context (AuthContext)
│ ├── pages/ # Main pages (Login, Dashboard, DatasetDetail)
│ ├── routes/ # Route configuration (index.tsx, ProtectedRoute.tsx)
│ ├── services/ # Axios configuration (api.ts)
│ ├── types/ # Type definitions (index.ts)
│ ├── App.tsx # Root component
│ └── main.tsx # React entry point
├── Dockerfile
└── nginx.conf # Nginx proxy configuration
```

## ⚙️ Proxy Configuration (Nginx)

This frontend does **not** require a `.env` file for the API URL, as Nginx handles all communication. The `nginx.conf` is configured to:

1.  Serve the React application as an SPA (Single Page Application).
2.  Redirect all API requests to the backend.
3.  Redirect all image requests (uploads) to the backend.
```
# frontend/nginx.conf

# API Proxy
location /api/ { 
proxy_pass http://backend:8000/;
}

# Image Proxy
location /uploads/ { 
proxy_pass http://backend:8000/uploads/;
}
```

## 🚀 How to Execute

This service is designed to be run with Docker Compose from the project root.

1. Build and Start the Containers:
```
docker-compose up --build
```

2. The application will be available at: http://localhost
