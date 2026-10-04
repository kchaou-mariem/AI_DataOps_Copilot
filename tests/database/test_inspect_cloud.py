# tests/database/test_inspect_cloud.py
import pytest
from dotenv import load_dotenv

pytestmark = pytest.mark.integration

load_dotenv(".env.cloud", override=True)

from backend.data_pipeline.loader import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    top_products = conn.execute(text("""
        SELECT p.name, COUNT(*) as nb_ventes
        FROM orders o JOIN products p ON o.product_id = p.id
        GROUP BY p.name ORDER BY nb_ventes DESC LIMIT 5
    """)).fetchall()
    print("Top produits vendus (Supabase) :", top_products)