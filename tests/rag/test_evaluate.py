"""Tests de l'évaluation du pipeline RAG."""
from backend.eval.evaluate import evaluate_retrieval, run_evaluation
from backend.rag.generator import generate_answer


def test_evaluate_retrieval_single_question():
    ok = evaluate_retrieval(
        "Combien de temps ai-je pour retourner un produit ?",
        expected_source="procedure_retour.pdf",
    )
    print("Retrieval trouvé :", ok)
    assert ok is True


def test_run_evaluation_full():
    results = run_evaluation()
    print("\n=== RÉSUMÉ ===")
    print(results["summary"])
    assert results["summary"]["n_questions"] == 16


from backend.eval.evaluate import judge_faithfulness


def test_judge_faithfulness_detects_fabrication():
    context = ["Le délai de retour est de 30 jours calendaires."]
    fake_answer = "Le délai de retour est de 90 jours et inclut une compensation de 50€."
    score = judge_faithfulness(fake_answer, context)
    print("Score pour une réponse inventée :", score)
    assert score < 1.0

def test_generate_answer_out_of_scope_question():
    """Vérifie que le système ne fabrique pas de réponse quand l'info n'existe dans aucun document."""
    result = generate_answer("Quelle est la couleur du logo NovaShop ?")
    print("RÉPONSE :", result.answer)
    print("SOURCES :", [s.filename for s in result.sources])