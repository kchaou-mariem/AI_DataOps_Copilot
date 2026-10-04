# tests/rag/test_generate_cloud.py
import pytest
from dotenv import load_dotenv


@pytest.mark.integration
def test_generate_cloud():
	load_dotenv(".env.cloud", override=True)
	from backend.rag.generator import generate_answer

	result = generate_answer("Combien de temps ai-je pour retourner un produit ?")
	print("RÉPONSE :", result.answer)
	print("SOURCES :", [s.filename for s in result.sources])