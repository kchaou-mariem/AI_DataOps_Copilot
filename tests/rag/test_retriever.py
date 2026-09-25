"""Tests du retriever RAG (Phase 1)."""
from backend.rag.retriever import search, get_all_chunks  # adapte le chemin si ton fichier a un autre nom que retriever.py

def test_search():
    results = search("Combien de temps ai-je pour retourner un produit ?", top_k=2)
    print(len(results), "chunks trouvés")
    for r in results:
        print(f"score={r.score:.3f} | {r.filename} p.{r.page} | {r.text[:80]}...")
    assert len(results) > 0

def test_search_top4():
    results = search("Combien de temps ai-je pour retourner un produit ?", top_k=4)
    print(len(results), "chunks trouvés")
    for r in results:
        print(f"score={r.score:.3f} | {r.filename} p.{r.page} | {r.text[:100]}...")



def test_dump_all_chunks_for_source():
    chunks = get_all_chunks(filename="procedure_retour.pdf")
    print(f"{len(chunks)} chunks trouvés pour ce document")
    for c in chunks:
        print(f"--- chunk (page {c.page}) ---")
        print(c.text)
        print()



def test_clear_collection():
    import os
    from qdrant_client import QdrantClient

    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", 6333))
    collection_name = os.getenv("QDRANT_COLLECTION", "documents")

    client = QdrantClient(host=host, port=port)
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)
    print("Collection supprimée.")


from backend.rag.retriever import search_with_rerank


def test_search_with_rerank():
    results = search_with_rerank("Combien de temps ai-je pour retourner un produit ?")
    print(len(results), "chunks trouvés après reranking")
    for r in results:
        print(f"score={r.score:.3f} | {r.filename} p.{r.page} | {r.text[:100]}...")
    assert len(results) > 0