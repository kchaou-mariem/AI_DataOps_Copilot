"""
Outils disponibles pour l'agent IA (Phase 2).

Chaque outil expose : un nom, une description (utilisée par le LLM pour choisir
quand l'appeler), et une fonction d'exécution.
"""
from sqlalchemy import text
from backend.data_pipeline.loader import get_engine


def get_schema_columns() -> dict[str, set[str]]:
    """Retourne les tables et colonnes réellement disponibles, à partir des modèles SQLAlchemy."""
    from backend.database.models import Base

    return {
        table.name: {col.name for col in table.columns}
        for table in Base.metadata.tables.values()
    }

def validate_query_columns(query: str, schema: dict[str, set[str]]) -> str | None:
    """Vérifie que les tables/colonnes référencées dans la requête existent bien."""
    import re

    query_lower = query.lower()

    mentioned_tables = re.findall(r"(?:from|join)\s+(\w+)", query_lower)
    known_tables = set(schema.keys())
    unknown_tables = [t for t in mentioned_tables if t not in known_tables]
    if unknown_tables:
        return f"Table(s) inexistante(s) : {', '.join(unknown_tables)}. Tables disponibles : {', '.join(known_tables)}."

    # Les alias définis avec "AS xxx" sont des noms inventés valides, à ne pas vérifier
    aliases = set(re.findall(r"\bas\s+([a-z_][a-z0-9_]*)", query_lower))

    all_known_columns = {col for cols in schema.values() for col in cols}
    sql_keywords = {"select", "from", "where", "join", "on", "group", "by", "order", "as",
                     "count", "sum", "avg", "limit", "and", "or", "desc", "asc", "distinct", "inner", "left"}
    candidates = re.findall(r"\b([a-z_][a-z0-9_]*)\b", query_lower)
    for word in candidates:
        if word in sql_keywords or word in known_tables or word in all_known_columns or word in aliases:
            continue
        if word.isdigit() or len(word) <= 2:
            continue
        return f"Colonne ou terme inconnu détecté : '{word}'. Vérifie le schéma des tables."

    return None


def sql_tool(query: str) -> str:
    """Exécute une requête SQL en lecture seule sur la base retail et retourne le résultat en texte."""
    query_clean = query.strip().rstrip(";")
    if not query_clean.lower().startswith("select"):
        return "Erreur : seules les requêtes SELECT sont autorisées."

    schema = get_schema_columns()
    validation_error = validate_query_columns(query_clean, schema)
    if validation_error:
        return f"[REQUÊTE REJETÉE - NE PAS CONSIDÉRER CE RÉSULTAT COMME VALIDE] {validation_error}"

    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query_clean))
            rows = result.fetchall()
            columns = result.keys()
    except Exception as e:
        return f"[ERREUR SQL - NE PAS CONSIDÉRER CE RÉSULTAT COMME VALIDE] {e}"

    if not rows:
        return "Aucun résultat."

    header = " | ".join(columns)
    lines = [header, "-" * len(header)]
    for row in rows[:20]:
        lines.append(" | ".join(str(v) for v in row))
    if len(rows) > 20:
        lines.append(f"... et {len(rows) - 20} lignes supplémentaires")

    return "\n".join(lines)
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

from backend.rag.generator import generate_answer


def rag_tool(question: str) -> str:
    """Recherche dans les documents internes (procédures, politiques, rapports) et répond avec les sources."""
    result = generate_answer(question)

    if not result.sources:
        return result.answer  # déjà le message "aucun document trouvé"

    sources = ", ".join(sorted(set(f"{s.filename} (p.{s.page})" for s in result.sources)))
    return f"{result.answer}\n\nSources : {sources}"


RAG_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "rag_tool",
        "description": (
            "Recherche dans les documents internes de l'entreprise NovaShop : procédure de retour produit, "
            "politique de livraison, règlement interne commercial, rapport trimestriel. "
            "Utilise cet outil pour des questions sur les procédures, politiques, règles ou informations "
            "qualitatives contenues dans ces documents (pas pour des données chiffrées de la base de données)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "La question à poser sur les documents internes.",
                }
            },
            "required": ["question"],
        },
    },
}

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