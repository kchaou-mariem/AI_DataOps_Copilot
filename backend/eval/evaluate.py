"""
Évalue la qualité du système RAG sur backend/eval/eval_dataset.json (Phase 1).

Métriques calculées :
    - Retrieval precision/recall : le bon chunk source a-t-il été récupéré ?
    - Faithfulness : la réponse générée est-elle fidèle au contexte récupéré ?
    - Answer relevance : la réponse répond-elle vraiment à la question posée ?

Usage :
    python -m backend.eval.evaluate
"""
import json
from pathlib import Path

EVAL_DATASET_PATH = Path(__file__).parent / "eval_dataset.json"


def load_eval_dataset() -> list[dict]:
    with open(EVAL_DATASET_PATH, encoding="utf-8") as f:
        return json.load(f)["questions"]


def run() -> dict:
    """Lance le pipeline RAG sur chaque question du dataset et calcule les scores agrégés."""
    questions = load_eval_dataset()
    results = []
    for item in questions:
        # TODO Phase 1 :
        #   1. appeler backend.rag.retriever.search(item["question"])
        #   2. vérifier si expected_source figure dans les sources récupérées -> retrieval score
        #   3. appeler backend.rag.generator.generate_answer(...)
        #   4. comparer la réponse générée à expected_answer (via RAGAS ou LLM-judge) -> faithfulness score
        results.append({"id": item["id"], "retrieval_score": None, "faithfulness_score": None})

    return {
        "n_questions": len(questions),
        "retrieval_precision": None,  # TODO : moyenne des retrieval_score
        "faithfulness": None,  # TODO : moyenne des faithfulness_score
        "details": results,
    }


if __name__ == "__main__":
    scores = run()
    print(json.dumps(scores, indent=2, ensure_ascii=False))
