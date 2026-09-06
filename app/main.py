from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from .security import authenticate, create_access_token, current_user, require_roles
from .rag import DOCUMENTS, Document, answer, retrieve

app = FastAPI(title="Enterprise RAG with RBAC", version="1.0.0")

class QueryRequest(BaseModel):
    query: str = Field(min_length=2, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=10)

class DocumentRequest(BaseModel):
    id: str
    title: str
    text: str = Field(min_length=1)
    allowed_roles: set[str] = {"viewer"}

@app.get("/health")
def health():
    return {"status": "ok"}

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
    if not payload.allowed_roles.issubset({"admin", "analyst", "viewer"}):
        raise HTTPException(status_code=400, detail="Unknown role")
    DOCUMENTS.append(Document(payload.id, payload.title, payload.text, payload.allowed_roles))
    return {"created": payload.id, "by": user["username"]}

@app.post("/query")
def query(payload: QueryRequest, user=Depends(current_user)):
    hits = retrieve(payload.query, user["role"], payload.top_k)
    result = answer(payload.query, user["role"])
    result["retrieved"] = hits
    return result
