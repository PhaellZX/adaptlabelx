# 1. Usar a imagem oficial do Python
FROM python:3.11-slim

# Instalar as dependências do sistema operacional (Linux)
# que são necessárias para o OpenCV (cv2)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 3. Definir o diretório de trabalho
WORKDIR /app

# 4. Copiar o ficheiro de requisitos
COPY requirements.txt .

# 5. Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar o resto do código
COPY . .

# 7. Expor a porta
EXPOSE 8000

# 8. O comando para executar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]