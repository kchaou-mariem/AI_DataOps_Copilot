"""
Outils disponibles pour l'agent IA (Phase 2).

Chaque outil expose : un nom, une description (utilisée par le LLM pour choisir
quand l'appeler), et une fonction d'exécution.
"""
from sqlalchemy import text
from backend.data_pipeline.loader import get_engine


def sql_tool(query: str) -> str:
    """Exécute une requête SQL en lecture seule sur la base retail et retourne le résultat en texte.

    Sécurité : rejette toute requête qui ne commence pas par SELECT, pour empêcher
    l'agent de modifier ou supprimer des données par erreur (ou par une requête mal générée).
    """
    query_clean = query.strip().rstrip(";")
    if not query_clean.lower().startswith("select"):
        return "Erreur : seules les requêtes SELECT sont autorisées."

    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_clean))
            rows = result.fetchall()
            columns = result.keys()
    except Exception as e:
        return f"Erreur SQL : {e}"

    if not rows:
        return "Aucun résultat."

    # Formatte le résultat en texte lisible pour le LLM
    header = " | ".join(columns)
    lines = [header, "-" * len(header)]
    for row in rows[:20]:  # limite à 20 lignes pour ne pas saturer le contexte du LLM
        lines.append(" | ".join(str(v) for v in row))
    if len(rows) > 20:
        lines.append(f"... et {len(rows) - 20} lignes supplémentaires")

    return "\n".join(lines)


# Description de l'outil au format attendu par le function calling (Ollama/OpenAI-compatible)
SQL_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "sql_tool",
        "description": (
            "Exécute une requête SQL SELECT sur la base de données retail NovaShop, "
            "qui contient 3 tables : customers (id, name, email, country, signup_date), "
            "products (id, name, category, price, stock), "
            "orders (id, customer_id, product_id, order_date, quantity, total_amount). "
            "Utilise cet outil pour répondre à des questions chiffrées sur les ventes, "
            "clients ou produits (comptages, sommes, moyennes, classements, filtres par date/pays)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "La requête SQL SELECT à exécuter (dialecte PostgreSQL).",
                }
            },
            "required": ["query"],
        },
    },
}

from backend.rag.retriever import search
from backend.rag.generator import generate_answer


from backend.rag.generator import generate_answer


def rag_tool(question: str) -> str:
    """Recherche dans les documents internes (procédures, politiques, rapports) et répond avec les sources."""
    result = generate_answer(question)

    if not result.sources:
        return result.answer  # déjà le message "aucun document trouvé"

    sources = ", ".join(sorted(set(f"{s.filename} (p.{s.page})" for s in result.sources)))
    return f"{result.answer}\n\nSources : {sources}"

from backend.data_pipeline.profiling import profile_table


def quality_tool(table_name: str) -> str:
    """Retourne un rapport de qualité (valeurs manquantes, doublons) pour une table."""
    report = profile_table(table_name)
    if "error" in report:
        return report["error"]

    lines = [
        f"Table : {report['table']} ({report['n_rows']} lignes)",
        f"Doublons : {report['n_duplicates']}",
        "Valeurs manquantes par colonne :",
    ]
    for col, pct in report["missing_values_pct"].items():
        lines.append(f"  - {col} : {pct}%")

    return "\n".join(lines)


QUALITY_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "quality_tool",
        "description": (
            "Analyse la qualité d'une table de la base de données (valeurs manquantes, doublons). "
            "Tables disponibles : customers, products, orders. "
            "Utilise cet outil pour des questions sur la fiabilité ou la complétude des données, "
            "pas pour des questions métier sur les ventes elles-mêmes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Le nom de la table à analyser : customers, products ou orders.",
                }
            },
            "required": ["table_name"],
        },
    },
}