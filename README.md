# 🏥 API de Gerenciamento de Consultas Médicas – Desafio Técnico Back-end | Lacrei Saúde

Esta API RESTful foi desenvolvida como parte do desafio técnico da **Lacrei Saúde**, com o objetivo de gerenciar **profissionais de saúde** e **consultas médicas**, com foco em **boas práticas de desenvolvimento, segurança e deploy em produção**.

---

## 🚀 Tecnologias Utilizadas

- **Python 3.11**
- **Django 4.2**
- **Django REST Framework**
- **PostgreSQL**
- **Docker + Docker Compose**
- **Amazon EC2** (deploy production + staging)

- **GitHub Actions** (CI/CD automatizado)
- **.env** para variáveis sensíveis
- **APITestCase** para testes automatizados
- **JWT Authentication**
- **Swagger/OpenAPI** (documentação)
- **SSL/HTTPS** com certificados autoassinados

---

## 🌐 Ambientes Deployados

### **Production Environment**
- **URL**: https://3.92.21.223:8000/
- **Branch**: `main`
- **IP**: 3.92.21.223

### **Staging Environment** 
- **URL**: https://54.146.210.114:8000/
- **Branch**: `develop`
- **IP**: 54.146.210.114

---

## 🛠️ Setup do Ambiente AWS EC2

### 1. Criar Instância EC2
- **AMI**: Amazon Linux 2023
- **Tipo**: t2.micro ou t3.small
- **Storage**: 20GB GP2
- **Key Pair**: Criar ou usar par de chaves existente

### 2. Configurar Security Group
**Regras de Entrada:**
- **Porta 22 (SSH)**: 0.0.0.0/0 - Para acesso SSH
- **Porta 8000 (HTTPs)**: 0.0.0.0/0 - Para acesso à API
- **Porta 5432 (PostgreSQL)**: 0.0.0.0/0 - Para banco de dados

### 3. Instalar Dependências na EC2
```bash
# Conectar na EC2
ssh -i sua-chave.pem ec2-user@IP_DA_EC2

# Instalar dependências
sudo yum update -y
sudo yum install -y git docker

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Iniciar e habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Adicionar usuário ao grupo docker
sudo usermod -a -G docker ec2-user

# Reiniciar sessão SSH
exit
ssh -i sua-chave.pem ec2-user@IP_DA_EC2
```

### 4. Configurar Ambiente
```bash
# Criar diretório da aplicação
sudo mkdir -p /app/lacrei-api
sudo chown ec2-user:ec2-user /app/lacrei-api
cd /app/lacrei-api
```

---

## 🔧 Configuração do Django

### **Settings Importantes:**
```python
# Em core/settings.py
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1', 
    '3.92.21.223',    # IP da Production
    '54.146.210.114', # IP da Staging
    '.amazonaws.com'
]

# Para HTTPS
SECURE_SSL_REDIRECT = False  # Gerenciado pelo runsslserver
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    'https://3.92.21.223:8000',
    'https://54.146.210.114:8000'
]
```

---

## 🐳 Setup com Docker (Local/Desenvolvimento)

### 1. Subir o ambiente
```bash
sudo docker compose up --build
```

### 2. Acessar o container para migração
```bash
sudo docker compose exec web bash
python manage.py migrate
```

### 3. API disponível em:
```
https://localhost:8000  (com SSL autoassinado)
```

---

## ✅ Endpoints Disponíveis

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|-------------|
| GET | `/api/profissionais/` | Lista profissionais | JWT Required |
| POST | `/api/profissionais/` | Cria profissional | JWT Required |
| GET | `/api/profissionais/<id>/` | Detalha profissional | JWT Required |
| PUT | `/api/profissionais/<id>/` | Atualiza profissional | JWT Required |
| DELETE | `/api/profissionais/<id>/` | Deleta profissional | JWT Required |
| GET | `/api/consultas/` | Lista consultas | JWT Required |
| POST | `/api/consultas/` | Cria consulta | JWT Required |
| GET | `/api/consultas/<id>/` | Detalha consulta | JWT Required |
| PUT | `/api/consultas/<id>/` | Atualiza consulta | JWT Required |
| DELETE | `/api/consultas/<id>/` | Deleta consulta | JWT Required |
---

## 🔁 CI/CD com GitHub Actions

### **Fluxo Automatizado:**
1. **Push para `develop`** → Deploy automático para Staging EC2
2. **Push para `main`** → Deploy automático para Production EC2
3. **Testes automatizados** executados no EC2 após deploy
4. **Health checks** verificam integridade da aplicação
5. **Rollback automático** em caso de falha

### **Features do CI/CD:**
- ✅ Testes automatizados no EC2
- ✅ Deploy com zero downtime
- ✅ Rollback automático
- ✅ Health checks inteligentes
- ✅ Notificações de erro

---

## 🧪 Testes com APITestCase

### Como rodar os testes:
```bash
# Localmente
python manage.py test

# No container
docker-compose exec web python manage.py test

# No EC2 (após deploy)
docker-compose exec web python manage.py test --verbosity=2
```

### Localização dos testes:
- `consultas/tests.py`
- `profissionais/tests.py`

### Cobertura de testes:
- CRUD completo de profissionais
- CRUD completo de consultas  
- Validações e relacionamentos
- Testes de integração
- Autenticação JWT

---

## 🔒 Segurança Implementada

- **HTTPS** com certificados SSL autoassinados
- **JWT Authentication** para todos os endpoints
- **CORS** configurado adequadamente
- **Environment variables** para dados sensíveis
- **Docker security** best practices
- **PostgreSQL** com conexões seguras

---

## 📋 Estratégia de Deploy

### **Branch Strategy:**
- **`develop`** → Staging Environment (testes)
- **`main`** → Production Environment (produção)

### **Rollback Automático:**
- Health checks monitoram integridade
- Rollback para commit anterior em caso de falha
- Backup automático do último commit estável

---

## 📁 Estrutura do Projeto

```
├── consultas/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── tests.py
├── profissionais/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── tests.py
├── core/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── setup_ssl.sh
└── README.md
```

---

## 🚀 Deploy Manual (Emergência)

```bash
# Conectar na EC2
ssh -i production-key.pem ec2-user@3.92.21.223

# Fazer deploy manual
cd /app/lacrei-api
git fetch origin main
git reset --hard origin/main
docker-compose down
docker-compose up --build -d
```

---

## ⚠️ Troubleshooting Comum

### **Erro de Conexão:**
```bash
# Verificar se containers estão rodando
docker-compose ps

# Verificar logs
docker-compose logs web

# Testar conexão com banco
docker-compose exec db psql -U postgres
```

### **Erro de SSL:**
```bash
# Gerar novos certificados
./setup_ssl.sh
```

---

## 🤝 Contato

Feito com 💙 por **Hugo** para a **Lacrei Saúde**.

- 📧 **Email**: hugodelima.dev@gmail.com
- 🔗 **LinkedIn**: [Hugo de Lima](https://linkedin.com/in/hugo-de-lima)
- 🐙 **GitHub**: [Hugodelima](https://github.com/Hugodelima)

---

## 📝 Licença

Este projeto foi desenvolvido como parte de um desafio técnico e é de uso educacional.

**⚠️ Nota**: Os IPs e URLs podem mudar conforme a infraestrutura evolui. Sempre verifique os IPs atuais no painel da AWS.