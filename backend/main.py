"""
Point d'entrée de l'API AI DataOps Copilot.

Lancer en local :
    uvicorn main:app --reload

Endpoints principaux (à mesure des phases) :
    Phase 1 : /rag/ingest, /rag/ask, /rag/evaluate
    Phase 2 : /agent/ask
    Phase 3 : /pipeline/upload (déclenché aussi par n8n)
"""
from fastapi import FastAPI
from backend.api.rag_routes import router as rag_router

app = FastAPI(
    title="AI DataOps Copilot",
    description="Plateforme RAG + Agentic AI + Automatisation pour données d'entreprise (retail).",
    version="0.1.0",
)

app.include_router(rag_router, prefix="/rag", tags=["RAG"])


@app.get("/health")
def health_check():
    """Endpoint de santé — utile pour Docker healthcheck et CI/CD."""
    return {"status": "ok"}
