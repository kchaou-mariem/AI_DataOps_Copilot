"""
Boucle d'exécution de l'agent (Phase 2).

Logique :
    1. Le LLM reçoit la question + la liste des outils disponibles (function calling)
    2. Il décide d'appeler un outil (ou de répondre directement)
    3. L'outil choisi est exécuté, son résultat est renvoyé au LLM
    4. Le LLM formule la réponse finale à partir de ce résultat
    (boucle possible si le LLM veut enchaîner plusieurs outils)
"""
import os
import json
from dataclasses import dataclass, field

import ollama

from backend.agents.tools import sql_tool, rag_tool, quality_tool, SQL_TOOL_SCHEMA, RAG_TOOL_SCHEMA, QUALITY_TOOL_SCHEMA

TOOLS_SCHEMA = [SQL_TOOL_SCHEMA, RAG_TOOL_SCHEMA, QUALITY_TOOL_SCHEMA]

TOOL_FUNCTIONS = {
    "sql_tool": sql_tool,
    "rag_tool": rag_tool,
    "quality_tool": quality_tool,
}

SYSTEM_PROMPT = """Tu es l'assistant IA de NovaShop, une entreprise de vente en ligne.
Tu as accès à 3 outils :
- sql_tool : pour les questions chiffrées sur les ventes, clients, produits (comptages, sommes, classements)
- rag_tool : pour les questions sur les procédures, politiques et documents internes
- quality_tool : pour les questions sur la fiabilité/complétude des données

Utilise l'outil approprié pour répondre. Si une question nécessite plusieurs informations,
tu peux appeler plusieurs outils successivement. Réponds toujours en français, de façon claire et concise."""


@dataclass
class AgentResponse:
    answer: str
    tool_calls: list[str] = field(default_factory=list)


def run_agent(question: str, max_steps: int = 8) -> AgentResponse:
    """Exécute la boucle agent : décision -> outil -> décision -> ... -> réponse finale."""
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")
    client = ollama.Client(host=host)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    tool_calls_log: list[str] = []

    for _ in range(max_steps):
        response = client.chat(model=model, messages=messages, tools=TOOLS_SCHEMA)
        message = response["message"]
        print("DEBUG message reçu :", message)  # ligne temporaire de debug
        messages.append(message)

        tool_calls = message.get("tool_calls")
        if not tool_calls:
            # Le LLM n'appelle plus d'outil -> c'est sa réponse finale
            return AgentResponse(answer=message["content"], tool_calls=tool_calls_log)

        # Exécute chaque outil demandé et renvoie le résultat au LLM
        for call in tool_calls:
            fn_name = call["function"]["name"]
            fn_args = call["function"]["arguments"]
            if isinstance(fn_args, str):
                fn_args = json.loads(fn_args)

            tool_calls_log.append(f"{fn_name}({fn_args})")

            fn = TOOL_FUNCTIONS.get(fn_name)
            result = fn(**fn_args) if fn else f"Outil inconnu : {fn_name}"

            messages.append({"role": "tool", "content": str(result)})

    return AgentResponse(
        answer="Désolé, je n'ai pas réussi à répondre après plusieurs tentatives.",
        tool_calls=tool_calls_log,
    )