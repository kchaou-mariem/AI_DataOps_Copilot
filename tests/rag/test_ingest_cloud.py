from dotenv import load_dotenv
load_dotenv(".env.cloud", override=True)

from backend.rag.ingestion import ingest_pdf

n = ingest_pdf("data/documents/procedure_retour.pdf")
print(f"{n} chunks ingérés dans Qdrant Cloud")