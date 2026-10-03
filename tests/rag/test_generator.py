"""Tests du générateur RAG (Phase 1)."""
import pytest

from backend.rag.generator import generate_answer, build_prompt
from backend.rag.retriever import RetrievedChunk


def test_build_prompt():
    chunks = [
        RetrievedChunk(text="Le délai est de 30 jours.", filename="test.pdf", page=1, score=1.0)
    ]
    prompt = build_prompt("Combien de temps ai-je pour retourner un produit ?", chunks)
    print(prompt)
    assert "30 jours" in prompt
    assert "test.pdf" in prompt


@pytest.mark.integration
def test_generate_answer_end_to_end():
    result = generate_answer("Combien de temps ai-je pour retourner un produit ?")
    print("RÉPONSE :", result.answer)
    print("SOURCES :", [s.filename for s in result.sources])
    assert result.answer
    assert len(result.sources) > 0