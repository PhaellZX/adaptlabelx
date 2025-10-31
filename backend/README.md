# 🐍 Backend (API) - AdaptLabelX

Esta pasta contém o serviço de API RESTful para a plataforma AdaptLabelX, construído com FastAPI.

## 🛠️ Stack Tecnológica

* **FastAPI:** Para a criação da API.
* **SQLAlchemy:** Para o ORM e comunicação com o banco de dados.
* **Pydantic:** Para validação de dados (agora na v2).
* **Ultralytics:** Para executar os modelos YOLOv8 e SAM.
* **PostgreSQL (Neon):** Banco de dados relacional.
* **JWT (passlib/jose):** Para autenticação de usuário.

## 📂 Estrutura de Pastas
```
backend/ 
├── app/ 
│ ├── api/ │
│ ├── dependencies.py 
│ │ └── endpoints/ # As rotas (ex: auth.py, datasets.py) 
│ ├── core/ 
│ │ ├── config.py # Configurações e .env
│ │ └── database.py # Conexão com o Neon DB 
│ ├── models/ # Modelos SQLAlchemy (Tabelas da BD)
│ ├── schemas/ # Modelos Pydantic (Validação)
│ ├── services/ # A lógica de negócio (ex: dataset_service.py) 
│ └── main.py # Ponto de entrada do FastAPI
├── ia_models/ # Modelos .pt padrão (yolov8n.pt, sam_b.pt) 
├── custom_models_user/ # Modelos .pt enviados pelos usuários
├── uploads/ # Imagens enviadas pelos usuários
├── Dockerfile 
├── requirements.txt
└── .env
```
## ⚙️ Variáveis de Ambiente

Para executar o backend, é necessário um ficheiro `.env` na raiz do projeto (junto ao `docker-compose.yml`) com as seguintes variáveis:

### dotenv:
Chave secreta para JWT (gere uma com 'openssl rand -hex 32')
```
SECRET_KEY=sua_chave_secreta_super_segura
```

### Configurações do JWT
```
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

URL de Conexão com o Banco de Dados (Neon)
Ex: postgresql://user:password@host.neon.tech/dbname?sslmode=require
```
DATABASE_URL=seu_url_do_neon_aqui
```

## 🚀 Como Executar
Este serviço é projetado para ser executado com o Docker Compose a partir da raiz do projeto.
1. Construir e Subir os Contêineres:
```
docker-compose up --build
```

2. A API estará disponível em: http://localhost:8000 (embora o Nginx faça o proxy a partir do http://localhost).

3. Documentação (Swagger): http://localhost:8000/docs