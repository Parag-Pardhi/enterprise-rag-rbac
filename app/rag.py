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
    scores = cosine_similarity(vectorizer.transform([query]), matrix)[0]
    ranked = sorted(zip(allowed, scores), key=lambda x: x[1], reverse=True)
    return [{"id": d.id, "title": d.title, "text": d.text, "score": float(score)} for d, score in ranked[:k]]


def grounded_answer(hits: list[dict]) -> dict:
    evidence = [h for h in hits if h["score"] > 0]
    if not evidence:
        return {"answer": "I could not find authorized evidence for that question.", "sources": []}
    context = " ".join(h["text"] for h in evidence)
    return {"answer": f"Grounded answer: {context}", "sources": [h["id"] for h in evidence]}


def answer(query: str, role: str, k: int = 3):
    return grounded_answer(retrieve(query, role, k))
