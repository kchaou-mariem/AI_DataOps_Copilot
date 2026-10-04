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
    import tempfile
    import os
    from backend.rag.ingestion import ingest_pdf

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        n_chunks = ingest_pdf(tmp_path)
    finally:
        os.remove(tmp_path)

    return {"filename": file.filename, "chunks_created": n_chunks}


@router.post("/ask", response_model=AskResponse)
async def ask_question(payload: AskRequest):
    """Pose une question au système RAG et retourne réponse + sources."""
    from backend.rag.generator import generate_answer

    result = generate_answer(payload.question, final_top_k=payload.top_k)

    sources = [
        Source(filename=s.filename, page=s.page, excerpt=s.text[:200])
        for s in result.sources
    ]

    return AskResponse(answer=result.answer, sources=sources)


@router.post("/evaluate")
async def run_evaluation():
    """Lance backend/eval/evaluate.py sur le jeu de test et retourne les scores."""
    # TODO Phase 1 : appeler backend.eval.evaluate.run
    raise NotImplementedError
