"""Tests du retriever RAG (Phase 1)."""
"""Tests du retriever RAG (Phase 1)."""
import pytest
import os
from backend.rag.ingestion import ingest_pdf
from backend.rag.retriever import search, search_with_rerank, get_all_chunks
from backend.rag.qdrant_utils import get_qdrant_client

@pytest.fixture(scope="module", autouse=True)
def ensure_data_ingested():
    """
    S'assure que la collection Qdrant contient des données avant de lancer
    les tests du retriever — évite l'erreur 'Collection doesn't exist' sur un
    environnement frais (nouvelle machine, CI/CD, volume Qdrant réinitialisé).
    """
    docs_dir = "data/documents"
    for filename in os.listdir(docs_dir):
        if filename.endswith(".pdf"):
            ingest_pdf(os.path.join(docs_dir, filename))
    yield

@pytest.mark.integration
def test_search():
    results = search("Combien de temps ai-je pour retourner un produit ?", top_k=2)
    print(len(results), "chunks trouvés")
    for r in results:
        print(f"score={r.score:.3f} | {r.filename} p.{r.page} | {r.text[:80]}...")
    assert len(results) > 0

@pytest.mark.integration
def test_search_top4():
    results = search("Combien de temps ai-je pour retourner un produit ?", top_k=4)
    print(len(results), "chunks trouvés")
    for r in results:
        print(f"score={r.score:.3f} | {r.filename} p.{r.page} | {r.text[:100]}...")



@pytest.mark.integration
def test_dump_all_chunks_for_source():
    chunks = get_all_chunks(filename="procedure_retour.pdf")
    print(f"{len(chunks)} chunks trouvés pour ce document")
    for c in chunks:
        print(f"--- chunk (page {c.page}) ---")
        print(c.text)
        print()



@pytest.mark.integration
def test_clear_collection():
    import os
    from qdrant_client import QdrantClient

    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", 6333))
    collection_name = os.getenv("QDRANT_COLLECTION", "documents")

    client = get_qdrant_client()
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
    print("Collection supprimée.")


from backend.rag.retriever import search_with_rerank


@pytest.mark.integration
def test_search_with_rerank():
    results = search_with_rerank("Combien de temps ai-je pour retourner un produit ?")
    print(len(results), "chunks trouvés après reranking")
    for r in results:
        print(f"score={r.score:.3f} | {r.filename} p.{r.page} | {r.text[:100]}...")
    assert len(results) > 0