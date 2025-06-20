# 1. Escolhe a imagem base (Python leve)
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /code

# 3. Instala dependências do sistema necessárias para o PostgreSQL funcionar com Python
RUN apt-get update && apt-get install -y libpq-dev

# 4. Copia o arquivo de dependências para o container
COPY requirements.txt .

# 5. Instala as dependências Python no ambiente do container
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia o restante da aplicação Django
COPY . .

# 7. Expõe a porta padrão do Django
EXPOSE 8000

# 8. Comando para rodar o servidor da aplicação
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:${PORT:-8000}"]


