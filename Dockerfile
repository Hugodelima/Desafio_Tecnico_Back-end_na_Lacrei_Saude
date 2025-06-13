# 1. Escolhe a imagem base (Python leve)
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /code

# 3. Instala dependências do sistema necessárias para o PostgreSQL funcionar com Python
RUN apt-get update && apt-get install -y libpq-dev netcat

# 4. Copia o arquivo de dependências para o container
COPY requirements.txt .

# 5. Instala as dependências Python no ambiente do container
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia o restante da aplicação Django
COPY . .

# 7. Expõe a porta padrão do Django (Render usará a variável PORT)
EXPOSE 8000

# 8. Comando para rodar migrações + iniciar o servidor
CMD ["sh", "-c", "while ! nc -z $DB_HOST $DB_PORT; do sleep 1; done && \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:${PORT:-8000}"]
