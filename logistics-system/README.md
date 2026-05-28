# Logistics System — Backend

## Stack

- **FastAPI** + **SQLAlchemy 2.x** + **PostgreSQL**
- **Alembic** para migrações
- **Pydantic v2** para validação
- **python-jose** para JWT

## Estrutura

```
backend/
├── app/
│   ├── core/           # Configurações, banco, segurança
│   │   ├── database.py
│   │   └── settings.py
│   ├── models/         # Entidades SQLAlchemy
│   ├── repositories/   # Acesso ao banco (queries)
│   ├── routers/        # Endpoints HTTP
│   ├── schemas/        # Pydantic (entrada/saída)
│   ├── services/       # Lógica de negócio
│   └── main.py
├── .env                # NÃO commitar
├── .env.example        # Template para novos devs
├── requirements.txt
└── docker-compose.yml
```

## Setup local

```bash
# 1. Crie o ambiente virtual
python -m venv venv && source venv/bin/activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure o .env
cp .env.example .env
# Edite .env com suas credenciais

# 4. Suba o banco via Docker
docker-compose up db -d

# 5. Rode as migrações
alembic upgrade head

# 6. Inicie a API
uvicorn app.main:app --reload
```

## Endpoints de infraestrutura

- `GET /health` — status da API e do banco
- `GET /docs` — Swagger UI (apenas em development)
