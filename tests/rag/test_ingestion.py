"""Tests du pipeline d'ingestion RAG (Phase 1)."""
import pytest


def test_placeholder():
    """Remplacer par de vrais tests une fois backend/rag/ingestion.py implémenté."""
    assert True

"""Tests du pipeline d'ingestion RAG (Phase 1)."""
from backend.rag.ingestion import extract_text_by_page


def test_extract_text_by_page():
    result = extract_text_by_page("data/documents/procedure_retour.pdf")
    print(len(result), "pages avec du texte")
    print(result[0])
    assert len(result) > 0


from backend.rag.ingestion import chunk_text


def test_chunk_text():
    text = "mot " * 1200  # simule un texte de 1200 mots
    chunks = chunk_text(text, page=1, filename="test.pdf")
    print(len(chunks), "chunks créés")
    print(chunks[0].chunk_id, "->", len(chunks[0].text.split()), "mots")
    assert len(chunks) > 1

from backend.rag.ingestion import embed_chunks, Chunk


def test_embed_chunks():
    chunks = [
        Chunk(text="Le délai de retour est de 30 jours.", filename="test.pdf", page=1, chunk_id="c1"),
        Chunk(text="La livraison standard prend 2 à 4 jours.", filename="test.pdf", page=1, chunk_id="c2"),
    ]
    embeddings = embed_chunks(chunks)
    print(len(embeddings), "embeddings créés, dimension:", len(embeddings[0]))
    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0

from backend.rag.ingestion import ingest_pdf


def test_ingest_pdf_end_to_end():
    n_chunks = ingest_pdf("data/documents/procedure_retour.pdf")
    print(n_chunks, "chunks ingérés dans Qdrant")
    assert n_chunks > 0


from backend.rag.ingestion import compute_chunk_size


def test_compute_chunk_size():
    size_small = compute_chunk_size(200)
    size_large = compute_chunk_size(2000)
    size_medium = compute_chunk_size(1200)

    print(f"200 mots -> chunk_size = {size_small}")
    print(f"2000 mots -> chunk_size = {size_large}")
    print(f"1200 mots -> chunk_size = {size_medium}")

    assert size_small == 100
    assert size_large == 500
    assert size_medium == 300