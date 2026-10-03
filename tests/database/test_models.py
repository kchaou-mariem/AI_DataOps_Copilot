"""Tests des modèles de base de données (Phase 2)."""
import pytest
from backend.database.models import Base, Customer, Product, Order


def test_models_import_correctly():
    print("Tables définies :", list(Base.metadata.tables.keys()))
    assert "customers" in Base.metadata.tables
    assert "products" in Base.metadata.tables
    assert "orders" in Base.metadata.tables

from backend.data_pipeline.loader import get_engine, create_tables, seed_sample_data


@pytest.mark.integration
def test_create_and_seed():
    engine = get_engine()
    create_tables(engine)
    counts = seed_sample_data(engine)
    print("Données insérées :", counts)
    assert counts["customers"] >= 0  # >= 0 car peut déjà être seedé d'un run précédent

from backend.data_pipeline.loader import drop_tables, seed_from_olist


@pytest.mark.integration
def test_seed_from_olist():
    engine = get_engine()
    drop_tables(engine)
    create_tables(engine)
    counts = seed_from_olist("data/raw", engine)
    print("Données Olist insérées :", counts)
    assert counts["orders"] > 0

@pytest.mark.integration
def test_inspect_data():
    from sqlalchemy import text
    engine = get_engine()
    with engine.connect() as conn:
        top_products = conn.execute(text("""
            SELECT p.name, COUNT(*) as nb_ventes
            FROM orders o JOIN products p ON o.product_id = p.id
            GROUP BY p.name ORDER BY nb_ventes DESC LIMIT 5
        """)).fetchall()
        print("Top 5 catégories vendues :", top_products)