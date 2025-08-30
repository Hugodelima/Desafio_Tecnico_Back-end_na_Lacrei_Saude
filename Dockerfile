FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema incluindo SSL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput

# Porta exposta
EXPOSE 8000

# Comando de inicialização com SSL
CMD sh -c "python manage.py migrate && python manage.py runsslserver 0.0.0.0:8000 --certificate /app/cert.pem --key /app/key.pem"