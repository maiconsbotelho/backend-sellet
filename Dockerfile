# Use imagem oficial Python
FROM python:3.10-slim

# Evita prompts de instalação
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Cria diretório de trabalho
WORKDIR /app

# Instala dependências básicas
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de dependência
COPY requirements.txt .

# Instala dependências do projeto
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia o restante do projeto
COPY . .

# Dá permissão ao script de entrada
RUN chmod +x ./entrypoint.sh

# Expõe a porta usada no Railway
EXPOSE 8080

# Usa script de entrada como comando inicial
ENTRYPOINT ["./entrypoint.sh"]
