from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from .rag import DOCUMENTS, Document, grounded_answer, retrieve
from .security import authenticate, create_access_token, current_user, require_roles

app = FastAPI(title="Enterprise RAG with RBAC", version="1.1.0")
ALLOWED_ROLES = {"admin", "analyst", "viewer"}


class QueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=10)


class DocumentRequest(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=10000)
    allowed_roles: set[str] = {"viewer"}


@app.get("/health")
def health():
    return {"status": "ok", "documents": len(DOCUMENTS)}


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": create_access_token({"sub": user["username"], "role": user["role"]}), "token_type": "bearer", "role": user["role"]}


@app.get("/documents")
def documents(user=Depends(current_user)):
    return [{"id": d.id, "title": d.title, "allowed_roles": sorted(d.allowed_roles)} for d in DOCUMENTS if user["role"] in d.allowed_roles]


@app.post("/documents")
def add_document(payload: DocumentRequest, user=Depends(require_roles("admin", "analyst"))):
    if not payload.allowed_roles or not payload.allowed_roles.issubset(ALLOWED_ROLES):
        raise HTTPException(status_code=400, detail="Unknown or empty role set")
    if any(d.id == payload.id for d in DOCUMENTS):
        raise HTTPException(status_code=409, detail="Document id already exists")
    DOCUMENTS.append(Document(payload.id, payload.title, payload.text, payload.allowed_roles))
    return {"created": payload.id, "by": user["username"]}


@app.post("/query")
def query(payload: QueryRequest, user=Depends(current_user)):
    hits = retrieve(payload.query, user["role"], payload.top_k)
    return {**grounded_answer(hits), "retrieved": hits}
