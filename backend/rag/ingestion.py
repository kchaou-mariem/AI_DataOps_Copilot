"""
Pipeline d'ingestion des documents (Phase 1).

Étapes :
    1. Extraction du texte du PDF (page par page, pour garder la métadonnée "page")
    2. Chunking (taille ~500 tokens, overlap ~50)
    3. Embeddings (sentence-transformers)
    4. Stockage dans Qdrant, avec métadonnées {filename, page}
"""

from dotenv import load_dotenv
load_dotenv()

from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    filename: str
    page: int
    chunk_id: str


def extract_text_by_page(pdf_path: str) -> list[tuple[int, str]]:
    """Retourne une liste (numéro_page, texte) via pdfplumber."""
    import pdfplumber

    pages_content: list[tuple[int, str]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                pages_content.append((page_num, text))
    return pages_content


# def chunk_text(text: str, page: int, filename: str, chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
#     """Découpe un texte en chunks avec chevauchement (découpage par mots)."""
#     words = text.split()
#     chunks: list[Chunk] = []
#     start = 0
#     chunk_index = 0

#     while start < len(words):
#         end = start + chunk_size
#         chunk_words = words[start:end]
#         chunk_str = " ".join(chunk_words)

#         chunks.append(Chunk(
#             text=chunk_str,
#             filename=filename,
#             page=page,
#             chunk_id=f"{filename}_p{page}_c{chunk_index}",
#         ))

#         chunk_index += 1
#         start += chunk_size - overlap  # on recule de `overlap` mots pour le chevauchement

#     return chunks

def compute_chunk_size(total_words: int, target_chunks: int = 4, min_size: int = 100, max_size: int = 500) -> int:
    """Calcule une taille de chunk adaptée à la longueur du document.

    Vise environ `target_chunks` chunks par document, borné entre min_size et max_size
    pour éviter des chunks trop petits (perte de contexte) ou trop grands (imprécision
    de la recherche vectorielle).
    """
    if total_words == 0:
        return min_size
    ideal_size = total_words // target_chunks
    return max(min_size, min(ideal_size, max_size))


def chunk_text(text: str, page: int, filename: str, chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Découpe un texte en chunks avec chevauchement (découpage par mots)."""
    words = text.split()
    chunks: list[Chunk] = []
    start = 0
    chunk_index = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_str = " ".join(chunk_words)

        chunks.append(Chunk(
            text=chunk_str,
            filename=filename,
            page=page,
            chunk_id=f"{filename}_p{page}_c{chunk_index}",
        ))

        chunk_index += 1
        start += chunk_size - overlap

    return chunks


def ingest_pdf(pdf_path: str) -> int:
    """Pipeline complet : extrait, découpe (taille adaptative), encode et stocke un PDF."""
    filename = pdf_path.split("/")[-1]
    pages = extract_text_by_page(pdf_path)

    total_words = sum(len(text.split()) for _, text in pages)
    chunk_size = compute_chunk_size(total_words)
    overlap = max(10, chunk_size // 10)  # overlap = 10% du chunk_size, minimum 10 mots

    all_chunks: list[Chunk] = []
    for page_num, text in pages:
        all_chunks.extend(chunk_text(text, page_num, filename, chunk_size=chunk_size, overlap=overlap))

    embeddings = embed_chunks(all_chunks)
    store_in_qdrant(all_chunks, embeddings)
    return len(all_chunks)

def embed_chunks(chunks: list[Chunk]) -> list[list[float]]:
    """Calcule les embeddings de chaque chunk via sentence-transformers."""
    import os #sert à récupérer la variable d'environnement EMBEDDING_MODEL
    from sentence_transformers import SentenceTransformer #sert à calculer les embeddings des chunks

    model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5") #récupère le nom du modèle d'embedding depuis la variable d'environnement EMBEDDING_MODEL, ou utilise un modèle par défaut
    model = SentenceTransformer(model_name) #charge le modèle d'embedding

    texts = [chunk.text for chunk in chunks] # récupère le texte de chaque chunk pour les passer au modèle d'embedding
    embeddings = model.encode(texts, show_progress_bar=False) # calcule les embeddings pour chaque chunk

    return embeddings.tolist()


def store_in_qdrant(chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    """Upsert les chunks + embeddings + métadonnées dans la collection Qdrant."""
    import os
    import uuid
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams

    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", 6333))
    collection_name = os.getenv("QDRANT_COLLECTION", "documents")

    client = QdrantClient(host=host, port=port)

    # Créer la collection si elle n'existe pas encore
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=len(embeddings[0]), distance=Distance.COSINE),
        )

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "text": chunk.text,
                "filename": chunk.filename,
                "page": chunk.page,
                "chunk_id": chunk.chunk_id,
            },
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]

    client.upsert(collection_name=collection_name, points=points)


# def ingest_pdf(pdf_path: str) -> int:
#     """Pipeline complet : extrait, découpe, encode et stocke un PDF. Retourne le nb de chunks créés."""
#     filename = pdf_path.split("/")[-1]
#     pages = extract_text_by_page(pdf_path)
#     all_chunks: list[Chunk] = []
#     for page_num, text in pages:
#         all_chunks.extend(chunk_text(text, page_num, filename))
#     embeddings = embed_chunks(all_chunks)
#     store_in_qdrant(all_chunks, embeddings)
#     return len(all_chunks)











