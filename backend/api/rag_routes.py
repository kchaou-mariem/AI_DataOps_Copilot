"""
Routes HTTP pour le module RAG (Phase 1).

À implémenter :
    POST /rag/ingest   -> ingère un ou plusieurs PDF (extraction, chunking, embeddings, stockage Qdrant)
    POST /rag/ask       -> reçoit une question, retourne réponse + sources
    POST /rag/evaluate  -> lance le jeu d'évaluation et retourne les scores
"""
from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    top_k: int = 4


class Source(BaseModel):
    filename: str
    page: int
    excerpt: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


@router.post("/ingest")
async def ingest_document(file: UploadFile):
    """Ingère un PDF : extraction -> chunking -> embeddings -> Qdrant."""
    # TODO Phase 1 : appeler backend.rag.ingestion.ingest_pdf
    raise NotImplementedError


@router.post("/ask", response_model=AskResponse)
async def ask_question(payload: AskRequest):
    """Pose une question au système RAG et retourne réponse + sources."""
    # TODO Phase 1 : appeler backend.rag.retriever puis backend.rag.generator
    raise NotImplementedError


@router.post("/evaluate")
async def run_evaluation():
    """Lance backend/eval/evaluate.py sur le jeu de test et retourne les scores."""
    # TODO Phase 1 : appeler backend.eval.evaluate.run
    raise NotImplementedError
