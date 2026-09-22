"""
Génération de la réponse à partir du contexte récupéré (Phase 1).
"""
from backend.rag.retriever import RetrievedChunk

PROMPT_TEMPLATE = """Tu es un assistant qui répond aux questions d'employés en te basant \
UNIQUEMENT sur le contexte fourni ci-dessous. Si la réponse ne figure pas dans le contexte, \
dis clairement que tu ne sais pas.

Contexte :
{context}

Question : {question}

Réponse :"""


def build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n".join(f"[{c.filename} - page {c.page}] {c.text}" for c in chunks)
    return PROMPT_TEMPLATE.format(context=context, question=question)


def generate_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    """Appelle le LLM (Ollama) avec le prompt construit et retourne la réponse brute."""
    prompt = build_prompt(question, chunks)
    # TODO : appeler le client ollama avec OLLAMA_MODEL (.env)
    raise NotImplementedError
