# 🏥 API de Gerenciamento de Consultas Médicas – Desafio Técnico Back-end | Lacrei Saúde

Esta API RESTful foi desenvolvida como parte do desafio técnico da **Lacrei Saúde**, com o objetivo de gerenciar **profissionais de saúde** e **consultas médicas**, com foco em **boas práticas de desenvolvimento, segurança e deploy em produção**.

---

## 🚀 Tecnologias Utilizadas

- **Python 3.11**
- **Django 4.2**
- **Django REST Framework**
- **PostgreSQL**
- **Docker + Docker Compose**
- **Render.com** (deploy)
- **GitHub Actions** (CI/CD)
- **.env** para variáveis sensíveis
- **APITestCase** para testes automatizados

---

## 🐳 Setup com Docker (recomendado)

### 1. Subir o ambiente
```bash
sudo docker compose up
```

### 2. Acessar o container para migração
```bash
sudo docker compose exec web bash
python manage.py migrate
python manage.py runserver
```

### 3. API disponível em:
```
http://localhost:8000/api/
```

---

## ✅ Endpoints Disponíveis

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/profissionais/` | Lista todos os profissionais |
| POST | `/api/profissionais/` | Cria um profissional |
| GET | `/api/profissionais/<id>/` | Detalha um profissional |
| PUT | `/api/profissionais/<id>/` | Atualiza um profissional |
| DELETE | `/api/profissionais/<id>/` | Deleta um profissional |
| GET | `/api/consultas/` | Lista todas as consultas |
| POST | `/api/consultas/` | Cria uma consulta |
| GET | `/api/consultas/<id>/` | Detalha uma consulta |
| PUT | `/api/consultas/<id>/` | Atualiza uma consulta |
| DELETE | `/api/consultas/<id>/` | Deleta uma consulta |
| GET | `/api/consultas/?profissional_id=<id>` | Filtra consultas por profissional |

---

## 🧪 Testes com APITestCase

### Como rodar os testes:
```bash
python manage.py test
```

### Localização dos testes:
- `consultas/tests.py`
- `profissionais/tests.py`

### Testes incluem:
- CRUD completo de profissionais
- CRUD completo de consultas
- Validações e relacionamentos
- Testes de integração

---

## ☁️ Deploy no Render

A aplicação foi publicada em produção utilizando **Render.com** com:

- Dockerfile personalizado
- Banco de dados PostgreSQL do próprio Render
- Configuração `.env` via painel
- CMD adaptado no Dockerfile para usar porta dinâmica:

```dockerfile
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:${PORT:-8000}"]
```

### 🔗 Link de Produção:
**[https://lacrei-api.onrender.com/api](https://lacrei-api.onrender.com/api/?format=json)**

---

## 🔁 CI/CD com GitHub Actions

O deploy é automatizado via **Render** (Web Service conectado ao GitHub), acionado a cada push na branch `main`.

---

## 💡 Decisões Técnicas

- **Django REST Framework**: Escolhido pela rapidez no desenvolvimento e boas práticas REST
- **Arquitetura por apps**: Divisão entre `profissionais` e `consultas` para melhor organização
- **PostgreSQL**: Banco relacional robusto e compatível com ambiente de produção
- **Variáveis de ambiente**: Uso de `.env` para garantir segurança de credenciais
- **Configurações de segurança**: `ALLOWED_HOSTS`, `DEBUG=False`, validação rigorosa de input
- **Docker**: Containerização para facilitar deploy e desenvolvimento

---
📊 Quadro do Projeto
Visão Geral do Quadro
![image](https://github.com/user-attachments/assets/2505eb72-b2f7-4463-9e8b-5556e12570b8)

---

## 🛠️ Melhorias Futuras

- [ ] Integração real com **Asaas** para pagamentos
- [ ] Autenticação via **JWT**
- [ ] Sistema de permissões (admin, recepção, etc.)
- [ ] Fluxo de rollback no deploy via GitHub Actions
- [ ] Implementação de logs estruturados
- [ ] Cache com Redis
- [ ] Documentação automática com Swagger/OpenAPI

---

## ❌ Erros Encontrados e Soluções

### 1. **Conexão recusada ao banco**
- **Problema**: API não conseguia conectar ao PostgreSQL
- **Solução**: Configuração correta das variáveis de ambiente e delay na inicialização

### 2. **Erro psycopg2 em host**
- **Problema**: Nome do host do banco incorreto no Docker
- **Solução**: Usar nome `db` igual ao serviço definido no docker-compose.yml

### 3. **"relation does not exist"**
- **Problema**: Tabelas não existiam em produção
- **Solução**: Executar migrations corretamente no ambiente de produção

### 4. **ALLOWED_HOSTS no Render**
- **Problema**: Django bloqueando requisições por host não permitido
- **Solução**: Configurar variável `ALLOWED_HOSTS` no painel do Render

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
├── lacrei_api/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
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
