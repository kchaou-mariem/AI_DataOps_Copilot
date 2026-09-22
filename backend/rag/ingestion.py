"""
Pipeline d'ingestion des documents (Phase 1).

Étapes :
    1. Extraction du texte du PDF (page par page, pour garder la métadonnée "page")
    2. Chunking (taille ~500 tokens, overlap ~50)
    3. Embeddings (sentence-transformers)
    4. Stockage dans Qdrant, avec métadonnées {filename, page}
"""
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    filename: str
    page: int
    chunk_id: str


def extract_text_by_page(pdf_path: str) -> list[tuple[int, str]]:
    """Retourne une liste (numéro_page, texte) via pdfplumber."""
    # TODO : implémenter avec pdfplumber
    raise NotImplementedError


def chunk_text(text: str, page: int, filename: str, chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Découpe un texte en chunks avec chevauchement."""
    # TODO : implémenter le découpage (tiktoken ou simple split par mots)
    raise NotImplementedError


def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    """Calcule les embeddings de chaque chunk via sentence-transformers."""
    # TODO : charger le modèle défini dans EMBEDDING_MODEL (.env)
    raise NotImplementedError


def store_in_qdrant(chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    """Upsert les chunks + embeddings + métadonnées dans la collection Qdrant."""
    # TODO : qdrant_client.upsert(...)
    raise NotImplementedError


def ingest_pdf(pdf_path: str) -> int:
    """Pipeline complet : extrait, découpe, encode et stocke un PDF. Retourne le nb de chunks créés."""
    filename = pdf_path.split("/")[-1]
    pages = extract_text_by_page(pdf_path)
    all_chunks: list[Chunk] = []
    for page_num, text in pages:
        all_chunks.extend(chunk_text(text, page_num, filename))
    embeddings = embed_chunks(all_chunks)
    store_in_qdrant(all_chunks, embeddings)
    return len(all_chunks)
