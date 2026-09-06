from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class Document:
    id: str
    title: str
    text: str
    allowed_roles: set[str]

DOCUMENTS = [
    Document("d1", "Engineering Runbook", "FastAPI services use health checks, structured logs, tests, and containerized deployment.", {"admin", "analyst"}),
    Document("d2", "Finance Policy", "Budget approvals require manager review and documented purchase justification.", {"admin", "analyst"}),
    Document("d3", "Company Handbook", "Employees should follow security, privacy, and acceptable-use policies.", {"admin", "analyst", "viewer"}),
]


def retrieve(query: str, role: str, k: int = 3):
    allowed = [d for d in DOCUMENTS if role in d.allowed_roles]
    if not allowed:
        return []
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([d.text for d in allowed])
    q = vectorizer.transform([query])
    scores = cosine_similarity(q, matrix)[0]
    ranked = sorted(zip(allowed, scores), key=lambda x: x[1], reverse=True)
    return [{"id": d.id, "title": d.title, "text": d.text, "score": float(score)} for d, score in ranked[:k]]

def answer(query: str, role: str):
    hits = retrieve(query, role)
    if not hits or hits[0]["score"] <= 0:
        return {"answer": "I could not find authorized evidence for that question.", "sources": []}
    context = " ".join(h["text"] for h in hits if h["score"] > 0)
    return {"answer": f"Grounded answer: {context}", "sources": [h["id"] for h in hits if h["score"] > 0]}
