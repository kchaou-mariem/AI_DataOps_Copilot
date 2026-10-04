from dotenv import load_dotenv
load_dotenv(".env.cloud", override=True)

from backend.rag.retriever import get_all_chunks

chunks = get_all_chunks(filename="procedure_retour.pdf")
print(f"{len(chunks)} chunks trouvés dans Qdrant Cloud")
for c in chunks:
    print(f"--- page {c.page} ---")
    print(c.text[:100])