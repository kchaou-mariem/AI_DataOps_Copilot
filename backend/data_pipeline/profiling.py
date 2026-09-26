"""
Data profiling des tables retail — utilisé par le quality_tool de l'agent (Phase 2).

Calcule : nb lignes, % valeurs manquantes par colonne, doublons, pour une table donnée.
"""
import pandas as pd
from backend.data_pipeline.loader import get_engine


def profile_table(table_name: str) -> dict:
    """Calcule un rapport de qualité pour une table (customers, products ou orders)."""
    allowed_tables = {"customers", "products", "orders"}
    if table_name not in allowed_tables:
        return {"error": f"Table inconnue. Tables disponibles : {', '.join(allowed_tables)}"}

    engine = get_engine()
    df = pd.read_sql_table(table_name, engine)

    n_rows = len(df)
    missing_pct = (df.isna().mean() * 100).round(2).to_dict()
    n_duplicates = int(df.duplicated().sum())

    return {
        "table": table_name,
        "n_rows": n_rows,
        "missing_values_pct": missing_pct,
        "n_duplicates": n_duplicates,
    }