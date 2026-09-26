"""Tests de l'orchestrateur agent (Phase 2)."""
from backend.agents.orchestrator import run_agent


def test_agent_sql_question():
    result = run_agent("Combien de commandes au total ?")
    print("Réponse :", result.answer)
    print("Outils appelés :", result.tool_calls)
    assert "sql_tool" in "".join(result.tool_calls)


def test_agent_rag_question():
    result = run_agent("Quel est le délai de retour d'un produit ?")
    print("Réponse :", result.answer)
    print("Outils appelés :", result.tool_calls)
    assert "rag_tool" in "".join(result.tool_calls)