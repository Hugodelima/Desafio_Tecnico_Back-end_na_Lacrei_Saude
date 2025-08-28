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
- **JWT Authentication**
- **Swagger/OpenAPI (documentação)**
---

## 🐳 Setup com Docker (recomendado)

### 1. Subir o ambiente
```bash
sudo docker compose up --build
```

### 2. Acessar o container para migração(se necessário)
```bash
sudo docker compose exec web bash
python manage.py migrate
```

### 3. API disponível em:
```
http://localhost:8000
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

## ☁️ Deploy no Render

A aplicação está em produção no Render.com no seguinte link:

**https://lacrei-api.onrender.com/**

---

## 🤝 Contato

Feito com 💙 por **Hugo** para a **Lacrei Saúde**.

- 📧 **Email**: hugodelima.dev@gmail.com
- 🔗 **LinkedIn**: [Hugo de Lima](https://linkedin.com/in/hugo-de-lima)
- 🐙 **GitHub**: [Hugodelima](https://github.com/Hugodelima)

---

## 📝 Licença

Este projeto foi desenvolvido como parte de um desafio técnico e é de uso educacional.
