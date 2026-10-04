"""
Évaluation du pipeline RAG (Phase 1).

Deux métriques :
    1. retrieval_precision : le bon document source a-t-il été retrouvé ?
       (comparaison de noms de fichiers, pas de LLM nécessaire)
    2. faithfulness : la réponse générée est-elle fondée sur le contexte récupéré ?
       (jugée par un LLM, via un prompt dédié)
"""
import json
import os

from backend.rag.retriever import search_with_rerank
from backend.rag.generator import generate_answer, GeneratedAnswer


def load_eval_dataset(path: str = "backend/eval/eval_dataset.json") -> list[dict]:
    """Charge le jeu de questions/réponses de référence depuis le fichier JSON."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]


def evaluate_retrieval(question: str, expected_source: str, top_k: int = 4) -> bool:
    """Vérifie si le fichier source attendu apparaît parmi les chunks récupérés."""
    results = search_with_rerank(question, final_top_k=top_k)
    retrieved_sources = [r.filename for r in results]
    return expected_source in retrieved_sources


JUDGE_PROMPT_TEMPLATE = """Voici un CONTEXTE et une RÉPONSE générée à partir de ce contexte.
Réponds UNIQUEMENT par un chiffre parmi : 0.0, 0.5 ou 1.0 — rien d'autre, pas de phrase.
- 1.0 si TOUT ce qui est affirmé dans la réponse est présent dans le contexte
- 0.5 si la réponse est partiellement fondée sur le contexte
- 0.0 si la réponse invente des informations absentes du contexte

CONTEXTE :
{context}

RÉPONSE :
{answer}

Score :"""


# def judge_faithfulness(answer: str, context_chunks: list[str]) -> float:
#     """Demande à un LLM de juger si la réponse est fidèle au contexte fourni."""
#     import ollama

#     host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
#     model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")

#     context = "\n\n".join(context_chunks)
#     prompt = JUDGE_PROMPT_TEMPLATE.format(context=context, answer=answer)

#     client = ollama.Client(host=host)
#     response = client.chat(
#         model=model,
#         messages=[{"role": "user", "content": prompt}],
#     )
#     raw_score = response["message"]["content"].strip()

#     # Le LLM peut parfois ajouter du texte malgré la consigne — on extrait le premier nombre trouvé
#     try:
#         return float(raw_score)
#     except ValueError:
#         import re
#         match = re.search(r"[01](?:\.[05])?", raw_score)
#         if match:
#             return float(match.group())
#         print(f"⚠️ Score de faithfulness non reconnu, réponse brute du juge : '{raw_score}' → traité comme 0.0")
#         return 0.0

def judge_faithfulness(answer: str, context_chunks: list[str]) -> float:
    """Demande à un LLM de juger si la réponse est fidèle au contexte fourni.
    Utilise Groq en cloud (si GROQ_API_KEY présent), sinon Ollama en local."""
    import os

    context = "\n\n".join(context_chunks)
    prompt = JUDGE_PROMPT_TEMPLATE.format(context=context, answer=answer)

    groq_api_key = os.getenv("GROQ_API_KEY")

    if groq_api_key:
        # Mode cloud : Groq (API compatible OpenAI)
        from openai import OpenAI
        client = OpenAI(
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_score = response.choices[0].message.content.strip()
    else:
        # Mode local : Ollama (comportement existant, inchangé)
        import ollama
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")
        client = ollama.Client(host=host)
        response = client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_score = response["message"]["content"].strip()

    # Le LLM peut parfois ajouter du texte malgré la consigne — on extrait le premier nombre trouvé
    try:
        return float(raw_score)
    except ValueError:
        import re
        match = re.search(r"[01](?:\.[05])?", raw_score)
        if match:
            return float(match.group())
        print(f"⚠️ Score de faithfulness non reconnu, réponse brute du juge : '{raw_score}' → traité comme 0.0")
        return 0.0
    
def run_evaluation(dataset_path: str = "backend/eval/eval_dataset.json") -> dict:
    """Lance l'évaluation complète sur toutes les questions du dataset."""
    questions = load_eval_dataset(dataset_path)

    retrieval_results = []
    faithfulness_results = []
    details = []

    for item in questions:
        question = item["question"]
        expected_source = item["expected_source"]

        # --- Retrieval ---
        retrieval_ok = evaluate_retrieval(question, expected_source)
        retrieval_results.append(retrieval_ok)

        # --- Faithfulness (nécessite une vraie réponse générée) ---
        result: GeneratedAnswer = generate_answer(question)
        context_texts = [chunk.text for chunk in result.sources]
        faithfulness_score = judge_faithfulness(result.answer, context_texts)
        faithfulness_results.append(faithfulness_score)

        details.append({
            "id": item["id"],
            "question": question,
            "expected_source": expected_source,
            "retrieval_ok": retrieval_ok,
            "generated_answer": result.answer,
            "faithfulness_score": faithfulness_score,
        })

        print(f"[{item['id']}] retrieval={'OK' if retrieval_ok else 'FAIL'} | faithfulness={faithfulness_score}")

    n = len(questions)
    summary = {
        "n_questions": n,
        "retrieval_precision": sum(retrieval_results) / n,
        "faithfulness": sum(faithfulness_results) / n,
    }

    return {"summary": summary, "details": details}


if __name__ == "__main__":
    results = run_evaluation()
    print("\n=== RÉSUMÉ ===")
    print(json.dumps(results["summary"], indent=2, ensure_ascii=False))