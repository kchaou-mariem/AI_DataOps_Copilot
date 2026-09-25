"""
Génération de réponses (Phase 1).

Étapes :
    1. Récupérer les chunks pertinents via search_with_rerank (retrieval + reranking)
    2. Construire un prompt combinant la question et le contexte récupéré
    3. Envoyer ce prompt au LLM (Ollama) pour générer une réponse rédigée
"""
from dataclasses import dataclass

from backend.rag.retriever import search_with_rerank, RetrievedChunk


@dataclass
class GeneratedAnswer:
    answer: str
    sources: list[RetrievedChunk]


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    """Construit le prompt envoyé au LLM, en injectant les chunks comme contexte."""
    context = "\n\n".join(
        f"[Source: {chunk.filename}, page {chunk.page}]\n{chunk.text}"
        for chunk in chunks
    )

    prompt = f"""Tu es un assistant qui répond aux questions UNIQUEMENT à partir du contexte fourni ci-dessous.
Si la réponse ne se trouve pas dans le contexte, dis clairement que tu ne sais pas — n'invente jamais d'information.

CONTEXTE :
{context}

QUESTION : {question}

RÉPONSE :"""

    return prompt


def call_llm(prompt: str) -> str:
    """Envoie le prompt au LLM via Ollama et retourne la réponse générée."""
    import os
    import ollama

    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")

    client = ollama.Client(host=host)
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    return response["message"]["content"]


def generate_answer(question: str, retrieval_top_k: int = 12, final_top_k: int = 4) -> GeneratedAnswer:
    """
    Pipeline complet : retrieval + reranking, puis génération de la réponse par le LLM.
    """
    chunks = search_with_rerank(question, retrieval_top_k=retrieval_top_k, final_top_k=final_top_k)

    if not chunks:
        return GeneratedAnswer(
            answer="Aucun document pertinent n'a été trouvé pour répondre à cette question.",
            sources=[],
        )

    prompt = build_prompt(question, chunks)
    answer_text = call_llm(prompt)

    return GeneratedAnswer(answer=answer_text, sources=chunks)