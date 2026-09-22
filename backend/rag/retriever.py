"""
Recherche vectorielle (Phase 1).

Étapes :
    1. Encoder la question avec le même modèle d'embeddings que l'ingestion
    2. Chercher les top-k chunks les plus proches dans Qdrant
    3. (optionnel) Re-ranking des résultats
"""
from dataclasses import dataclass


@dataclass
class RetrievedChunk:
    text: str
    filename: str
    page: int
    score: float


def embed_query(question: str) -> list[float]:
    """Encode la question utilisateur avec le modèle d'embeddings."""
    # TODO : réutiliser le même modèle que backend/rag/ingestion.py
    raise NotImplementedError


def search(question: str, top_k: int = 4) -> list[RetrievedChunk]:
    """Recherche les chunks les plus pertinents dans Qdrant."""
    # TODO : qdrant_client.search(...)
    raise NotImplementedError


def rerank(question: str, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
    """(Optionnel) Réordonne les chunks récupérés pour améliorer la pertinence."""
    # TODO : cross-encoder ou heuristique simple, à ajouter si le temps le permet
    return chunks
