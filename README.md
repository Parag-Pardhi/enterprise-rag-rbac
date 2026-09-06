# Enterprise RAG with RBAC

A production-oriented reference implementation of Retrieval-Augmented Generation with document-level role-based access control. The API authenticates users, filters retrieval by authorization metadata, and generates grounded answers from permitted documents.

## Architecture
`Client -> FastAPI -> JWT authentication -> RBAC filter -> Retriever -> Context -> LLM adapter`

The default retrieval engine is local and deterministic, so the project can be demonstrated without an external LLM API.

## Features
- JWT authentication
- Roles: `admin`, `analyst`, `viewer`
- Document ownership/role authorization
- Local TF-IDF retrieval baseline
- FastAPI REST endpoints
- Pydantic schemas
- Docker support
- Unit tests
- No secrets committed

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open `/docs` for Swagger UI.

Demo users are created by the application for local development. Change credentials and JWT configuration before any real deployment.

## API
- `POST /auth/login` — obtain JWT
- `GET /documents` — list documents allowed for the current role
- `POST /documents` — add an authorized document
- `POST /query` — retrieve authorized context and generate a grounded response
- `GET /health` — health check

## Security notes
This is a reference/portfolio implementation. Production deployments should use a managed identity provider, persistent database, encrypted secrets, audit logging, rate limiting, network controls, and a vetted embedding/vector infrastructure.