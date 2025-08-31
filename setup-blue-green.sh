#!/bin/bash
# Script de configuração inicial para Blue/Green Deployment

echo "🎯 Configurando Blue/Green Deployment para Lacrei Saúde"

# 1. Instalar Nginx
echo "📦 Instalando Nginx..."
sudo yum install nginx -y

# 2. Configurar Nginx
echo "⚙️ Configurando Nginx..."
sudo bash -c 'cat > /etc/nginx/nginx.conf << EOF
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log;
pid /run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    log_format  main  '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                      '\$status \$body_bytes_sent "\$http_referer" '
                      '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   65;
    types_hash_max_size 4096;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    # Configuração do Lacrei API
    include /etc/nginx/conf.d/lacrei-api.conf;
}
EOF'

# 3. Criar diretórios dos ambientes
echo "📁 Criando diretórios dos ambientes..."
sudo mkdir -p /app/blue /app/green
sudo chown ec2-user:ec2-user /app/blue /app/green

# 4. Configurar ambiente inicial
echo "🌱 Configurando ambiente inicial (blue)..."
cd /app/blue
git clone https://github.com/Hugodelima/Desafio_Tecnico_Back-end_na_Lacrei_Saude.git lacrei-api || true
cd lacrei-api

# 5. Gerar certificados SSL
echo "🔐 Gerando certificados SSL..."
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem \
  -keyout key.pem \
  -days 365 \
  -subj "/C=BR/ST=Sao_Paulo/L=Sao_Paulo/O=Lacrei_Saude/CN=localhost"

# 6. Configurar Nginx inicial
echo "⚙️ Configurando Nginx para blue..."
sudo bash -c 'cat > /etc/nginx/conf.d/lacrei-api.conf << EOF
upstream lacrei_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://lacrei_api;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF'

# 7. Iniciar Nginx
echo "🚀 Iniciando Nginx..."
sudo systemctl enable nginx
sudo systemctl start nginx
sudo nginx -t && sudo nginx -s reload

# 8. Marcar ambiente inicial
echo "blue" | sudo tee /app/current_environment > /dev/null

echo "✅ Configuração Blue/Green completa!"
echo ""
echo "📋 Próximos passos:"
echo "1. 🔧 Configure as secrets no GitHub"
echo "2. 🚀 Faça push para main para primeiro deploy"
echo "3. 📊 Verifique o health monitoring"
echo ""
echo "🌐 URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/"