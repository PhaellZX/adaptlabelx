# 🐍 Backend (API) - AdaptLabelX

This folder contains the RESTful API service for the AdaptLabelX platform, built with FastAPI.

## 🛠️ Technology Stack

* **FastAPI:** For creating the API.
* **SQLAlchemy:** For ORM and database communication.
* **Pydantic:** For data validation (now on v2).
* **Ultralytics:** To run YOLOv8 and SAM models.
* **PostgreSQL (Neon):** Relational database.
* **JWT (passlib/jose):** For user authentication.

## 📂 Folder Structure
```
backend/
├── app/
│ ├── api/ │
│ ├── dependencies.py
│ │ └── endpoints/ # Routes (e.g., auth.py, datasets.py)
│ ├── core/
│ │ ├── config.py # Configuration and .env
│ │ └── database.py # Neon DB connection
│ ├── models/ # SQLAlchemy models (DB tables)
│ ├── schemas/ # Pydantic models (validation)
│ ├── services/ # Business logic (e.g., dataset_service.py)
│ └── main.py # FastAPI entry point
├── ia_models/ # Standard .pt models (yolov8n.pt, sam_b.pt)
├── custom_models_user/ # User-uploaded .pt models
├── uploads/ # User-uploaded images
├── Dockerfile
├── requirements.txt
└── .env
```
## ⚙️ Environment Variables

To run the backend, a `.env` file is required in the project root (alongside `docker-compose.yml`) with the following variables:

### dotenv:
Secret key for JWT
Generate one using (Windows: 'openssl rand -hex 32') OR (Linux: 'head -c 32 /dev/urandom | base64')
```
SECRET_KEY=sua_chave_secreta_super_segura
```

### JWT Settings
```
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Database Connection URL (Neon)
Ex: postgresql://user:password@host.neon.tech/dbname?sslmode=require
```
DATABASE_URL=seu_url_do_neon_aqui
```

## 🚀 How to Execute
This service is designed to be run with Docker Compose from the project root.

1. Build and Start the Containers:
```
docker-compose up --build
```

2. The API will be available at: http://localhost:8000 (although Nginx proxies it from http://localhost).

3. Documentation (Swagger): http://localhost:8000/docs
