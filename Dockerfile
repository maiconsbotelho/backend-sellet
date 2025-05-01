# Imagem base segura e atualizada
FROM python:3.12-slim-bookworm

# Evita criação de arquivos .pyc e garante log em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define diretório de trabalho
WORKDIR /app

# Instala dependências básicas do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia apenas o requirements.txt e instala pacotes Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia o restante do projeto
COPY . .

# Coleta arquivos estáticos durante o build da imagem
RUN python manage.py collectstatic --noinput

# Dá permissão ao script de entrada
RUN chmod +x ./entrypoint.sh

# Expõe a porta usada no Railway
EXPOSE 8080

# Comando de entrada
ENTRYPOINT ["./entrypoint.sh"]
