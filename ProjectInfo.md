## 📘 API Documentation

Com o servidor rodando (Docker ou local), acesse:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🚀 Template setup

1. Copie o arquivo de variáveis:

```bash
cp .env.example .env
```

2. Ajuste os valores de usuário/senha no `.env` (Postgres, JWT e PgAdmin).
3. Suba o projeto:

```bash
docker compose up --build
```

Esse projeto foi preparado para funcionar como template, centralizando configurações em variáveis de ambiente.

---

## 🔐 Authentication

1. Vá para [http://localhost:8000/docs](http://localhost:8000/docs)
2. Use o endpoint `/oauth2/login` para gerar token.
3. Clique em **Authorize** e informe o token bearer.
