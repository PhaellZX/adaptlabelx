# frontend/Dockerfile

# --- STAGE 1: Construir a aplicação React ---
FROM node:18-alpine AS build

# Definir o diretório de trabalho
WORKDIR /app

# Copiar o package.json e package-lock.json
COPY package.json ./
COPY package-lock.json ./

# Instalar as dependências
RUN npm install

# Copiar o resto do código-fonte
COPY . .

# Construir a aplicação para produção
RUN npm run build

# --- STAGE 2: Servir com Nginx ---
FROM nginx:1.25-alpine

# Copiar os ficheiros estáticos construídos do Stage 1
# A app React é construída na pasta /app/dist
COPY --from=build /app/dist /usr/share/nginx/html

# Remover a configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copiar a nossa própria configuração do Nginx (vamos criar a seguir)
COPY nginx.conf /etc/nginx/conf.d

# Expor a porta 80 (porta padrão do Nginx)
EXPOSE 80

# O comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]