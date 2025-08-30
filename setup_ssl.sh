#!/bin/bash
# Script para configurar SSL no Django

echo "🚀 Configurando SSL para Django..."

# Verificar se os certificados existem
if [ ! -f "cert.pem" ] || [ ! -f "key.pem" ]; then
    echo "📝 Criando certificados SSL autoassinados..."
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/C=BR/ST=SaoPaulo/L=SaoPaulo/O=Lacrei/CN=localhost"
    echo "✅ Certificados criados: cert.pem e key.pem"
else
    echo "✅ Certificados já existem"
fi

echo "🔧 Configuração SSL concluída!"