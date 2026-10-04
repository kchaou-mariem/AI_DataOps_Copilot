"""
Recherche vectorielle (Phase 1).

Étapes :
    1. Encoder la question avec le même modèle d'embeddings que l'ingestion
    2. Chercher les top-k chunks les plus proches dans Qdrant
    3. (optionnel) Re-ranking des résultats
"""
from dataclasses import dataclass
from backend.rag.qdrant_utils import get_qdrant_client

@dataclass
class RetrievedChunk:
    text: str
    filename: str
    page: int
    score: float

def embed_query(question: str) -> list[float]:
    """Encode la question — Cohere en cloud, sinon sentence-transformers en local."""
    import os

    cohere_api_key = os.getenv("COHERE_API_KEY")

    if cohere_api_key:
        import cohere
        co = cohere.ClientV2(api_key=cohere_api_key)
        response = co.embed(
            texts=[question],
            model="embed-multilingual-v3.0",
            input_type="search_query",
            embedding_types=["float"],
        )
        return response.embeddings.float_[0]

    from sentence_transformers import SentenceTransformer
    model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    model = SentenceTransformer(model_name)
    return model.encode(question).tolist()

def search(question: str, top_k: int = 4) -> list[RetrievedChunk]:
    """Recherche les chunks les plus pertinents dans Qdrant."""
    import os
    from qdrant_client import QdrantClient

    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", 6333))
    collection_name = os.getenv("QDRANT_COLLECTION", "documents")

    client = get_qdrant_client()
    query_vector = embed_query(question)

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
    ).points

    return [
        RetrievedChunk(
            text=point.payload["text"],
            filename=point.payload["filename"],
            page=point.payload["page"],
            score=point.score,
        )
        for point in results
    ]


def rerank(question: str, chunks: list[RetrievedChunk], top_k: int = 4) -> list[RetrievedChunk]:
    """Réordonne les chunks — Cohere Rerank en cloud, cross-encoder local sinon."""
    import os

    if not chunks:
        return chunks

    cohere_api_key = os.getenv("COHERE_API_KEY")

    if cohere_api_key:
        import cohere
        co = cohere.ClientV2(api_key=cohere_api_key)
        documents = [chunk.text for chunk in chunks]
        response = co.rerank(
            model="rerank-multilingual-v3.0",
            query=question,
            documents=documents,
            top_n=top_k,
        )
        result = [
            RetrievedChunk(
                text=chunks[r.index].text,
                filename=chunks[r.index].filename,
                page=chunks[r.index].page,
                score=r.relevance_score,
            )
            for r in response.results
        ]
        return result

    # Mode local : cross-encoder sentence-transformers (comportement existant)
    import os as os_local
    from sentence_transformers import CrossEncoder

    model_name = os_local.getenv("RERANKER_MODEL", "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
    model = CrossEncoder(model_name)

    pairs = [(question, chunk.text) for chunk in chunks]
    scores = model.predict(pairs)

    reranked = sorted(zip(chunks, scores), key=lambda pair: pair[1], reverse=True)

    result = [
        RetrievedChunk(text=chunk.text, filename=chunk.filename, page=chunk.page, score=float(cross_score))
        for chunk, cross_score in reranked
    ]
    return result[:top_k]


def get_all_chunks(filename: str) -> list[RetrievedChunk]:
    """
    Récupère TOUS les chunks indexés pour un fichier donné,
    sans recherche par similarité — juste un scroll filtré par payload.
    Utile pour vérifier ce qui a réellement été indexé (debug du chunking/ingestion).
    """
    import os
    from qdrant_client import QdrantClient
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", 6333))
    collection_name = os.getenv("QDRANT_COLLECTION", "documents")

    client = get_qdrant_client()

    points, _ = client.scroll(
        collection_name=collection_name,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="filename",
                    match=MatchValue(value=filename)
                )
            ]
        ),
        limit=1000,  # large pour être sûr de tout récupérer
        with_payload=True,
        with_vectors=False,
    )

    return [
        RetrievedChunk(
            text=point.payload["text"],
            filename=point.payload["filename"],
            page=point.payload["page"],
            score=0.0,  # pas de score puisque ce n'est pas une recherche par similarité
        )
        for point in points
    ]

def search_with_rerank(question: str, retrieval_top_k: int = 12, final_top_k: int = 4) -> list[RetrievedChunk]:
    """
    Pipeline complet : retrieval large (embedding cosinus) puis reranking précis (cross-encoder).
    """
    candidates = search(question, top_k=retrieval_top_k)
    return rerank(question, candidates, top_k=final_top_k)