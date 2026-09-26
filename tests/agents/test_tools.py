"""Tests des outils de l'agent (Phase 2)."""
from backend.agents.tools import sql_tool


def test_sql_tool_valid_query():
    result = sql_tool("SELECT COUNT(*) as total FROM orders")
    print(result)
    assert "total" in result


def test_sql_tool_rejects_non_select():
    result = sql_tool("DELETE FROM orders")
    print(result)
    assert "Erreur" in result


def test_sql_tool_top_categories():
    result = sql_tool("""
        SELECT p.category, COUNT(*) as nb
        FROM orders o JOIN products p ON o.product_id = p.id
        GROUP BY p.category ORDER BY nb DESC LIMIT 3
    """)
    print(result)
    assert "cama_mesa_banho" in result or "beleza_saude" in result

from backend.agents.tools import rag_tool


def test_rag_tool():
    result = rag_tool("Quel est le délai de retour d'un produit ?")
    print(result)
    assert "30 jours" in result or "jours" in result

from backend.agents.tools import quality_tool


def test_quality_tool():
    result = quality_tool("orders")
    print(result)
    assert "Table : orders" in result


def test_quality_tool_invalid_table():
    result = quality_tool("invented_table")
    print(result)
    assert "inconnue" in result