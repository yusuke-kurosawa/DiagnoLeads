# DiagnoLeads Backend API

FastAPI backend for DiagnoLeads multi-tenant assessment platform.

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy 2.0
- **Cache**: Redis (Upstash)
- **AI**: Anthropic Claude API

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp ../.env.example .env
```

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Start Development Server

```bash
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000

- **Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Development

### Run Tests

```bash
pytest
pytest --cov=app  # With coverage
```

### Code Formatting

```bash
ruff format .
ruff check .
mypy .
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Config, middleware, database
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   │   └── ai/          # AI services (Claude)
│   └── main.py          # FastAPI app
├── alembic/             # Database migrations
├── tests/               # Test files
└── requirements.txt
```

## Multi-Tenant Architecture

All database queries are automatically scoped to the tenant via:

1. **JWT Token**: Contains `tenant_id` claim
2. **Middleware**: Extracts `tenant_id` and sets context
3. **Database**: Row-Level Security (RLS) enforces isolation

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
