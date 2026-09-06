from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def token(username, password):
    r = client.post("/auth/login", data={"username": username, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]

def test_viewer_cannot_create_document():
    t = token("viewer", "viewer123")
    r = client.post("/documents", headers={"Authorization": f"Bearer {t}"}, json={"id":"x","title":"x","text":"x","allowed_roles":["viewer"]})
    assert r.status_code == 403

def test_viewer_gets_only_authorized_documents():
    t = token("viewer", "viewer123")
    r = client.get("/documents", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 200
    assert [d["id"] for d in r.json()] == ["d3"]

def test_query_requires_authentication():
    r = client.post("/query", json={"query":"security"})
    assert r.status_code == 401
