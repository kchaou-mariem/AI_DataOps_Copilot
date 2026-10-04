import pytest
from dotenv import load_dotenv


@pytest.mark.integration
def test_ingest_cloud():
	load_dotenv(".env.cloud", override=True)
	from backend.rag.ingestion import ingest_pdf

	n = ingest_pdf("data/documents/procedure_retour.pdf")
	print(f"{n} chunks ingérés dans Qdrant Cloud")