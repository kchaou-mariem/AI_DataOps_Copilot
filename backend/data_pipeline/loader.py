"""
Chargement des tables customers, products, orders dans PostgreSQL,
et création du schéma s'il n'existe pas encore.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.models import Base, Customer, Product, Order


def get_engine():
    """Construit l'engine SQLAlchemy — utilise DATABASE_URL si présent (Supabase/cloud),
    sinon reconstruit l'URL à partir des variables POSTGRES_* individuelles (local)."""
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Mode cloud (Supabase) : URL complète déjà fournie, SSL requis
        return create_engine(database_url)

    # Mode local : reconstruction classique à partir des variables individuelles
    user = os.getenv("POSTGRES_USER", "dataops")
    password = os.getenv("POSTGRES_PASSWORD", "changeme")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "dataops_copilot")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)


def create_tables(engine) -> None:
    """Crée les tables définies dans models.py si elles n'existent pas déjà."""
    Base.metadata.create_all(engine)


def seed_sample_data(engine) -> dict:
    """Insère un petit jeu de données retail de test (à remplacer par le dataset Olist plus tard)."""
    Session = sessionmaker(bind=engine)
    session = Session()

    counts = {
        "customers": session.query(Customer).count(),
        "products": session.query(Product).count(),
        "orders": session.query(Order).count(),
    }
    if any(counts.values()):
        session.close()
        return counts  # déjà des données, on n'insère pas de doublons

    customers = [
        Customer(id=1, name="Alice Martin", email="alice@example.com", country="France", signup_date="2025-01-15"),
        Customer(id=2, name="Karim Bensaid", email="karim@example.com", country="France", signup_date="2025-03-02"),
        Customer(id=3, name="Lena Fischer", email="lena@example.com", country="Allemagne", signup_date="2025-05-20"),
    ]
    products = [
        Product(id=1, name="Sneakers Urban Line", category="Chaussures", price=79.90, stock=150),
        Product(id=2, name="Sac à dos CityPack", category="Accessoires", price=49.90, stock=80),
        Product(id=3, name="Veste légère AeroShell", category="Vêtements", price=99.90, stock=40),
    ]
    session.add_all(customers + products)
    session.commit()

    orders = [
        Order(id=1, customer_id=1, product_id=1, order_date="2026-07-10", quantity=1, total_amount=79.90),
        Order(id=2, customer_id=2, product_id=2, order_date="2026-08-05", quantity=2, total_amount=99.80),
        Order(id=3, customer_id=1, product_id=3, order_date="2026-09-12", quantity=1, total_amount=99.90),
        Order(id=4, customer_id=3, product_id=1, order_date="2026-09-18", quantity=1, total_amount=79.90),
    ]
    session.add_all(orders)
    session.commit()
    session.close()

    return {"customers": len(customers), "products": len(products), "orders": len(orders)}

def drop_tables(engine) -> None:
    """Supprime les tables existantes — nécessaire si le schéma a changé (ex. type des id)."""
    Base.metadata.drop_all(engine)


def seed_from_olist(raw_dir: str, engine, sample_size: int = 5000) -> dict:
    """Charge un échantillon du dataset Olist dans customers/products/orders.

    sample_size limite le nombre de lignes order_items traitées, pour garder
    un jeu de données démontrable rapidement (le dataset complet fait ~110k commandes).
    """
    import pandas as pd

    customers_df = pd.read_csv(f"{raw_dir}/olist_customers_dataset.csv")
    products_df = pd.read_csv(f"{raw_dir}/olist_products_dataset.csv")
    orders_df = pd.read_csv(f"{raw_dir}/olist_orders_dataset.csv")
    items_df = pd.read_csv(f"{raw_dir}/olist_order_items_dataset.csv")

    # On échantillonne au niveau des commandes (pas des lignes) pour garder des commandes complètes
    sampled_order_ids = orders_df["order_id"].drop_duplicates().sample(
        n=min(sample_size, len(orders_df)), random_state=42
    )
    orders_df = orders_df[orders_df["order_id"].isin(sampled_order_ids)]
    items_df = items_df[items_df["order_id"].isin(sampled_order_ids)]

    # Fusionne order_items avec orders pour récupérer customer_id et date d'achat
    merged = items_df.merge(orders_df[["order_id", "customer_id", "order_purchase_timestamp"]], on="order_id")

    # ---- customers ----
    used_customer_ids = merged["customer_id"].unique()
    cust_subset = customers_df[customers_df["customer_id"].isin(used_customer_ids)].copy()
    first_order_date = merged.groupby("customer_id")["order_purchase_timestamp"].min()

    customers_records = [
        {
            "id": row.customer_id,
            "name": f"Client {row.customer_id[:8]}",
            "email": f"{row.customer_id[:8]}@example.com",
            "country": "Brésil",
            "signup_date": pd.to_datetime(first_order_date.get(row.customer_id)).date(),
        }
        for row in cust_subset.itertuples()
    ]

    # ---- products ----
    used_product_ids = merged["product_id"].unique()
    prod_subset = products_df[products_df["product_id"].isin(used_product_ids)].copy()
    avg_price = merged.groupby("product_id")["price"].mean()

    products_records = [
        {
            "id": row.product_id,
            "name": row.product_category_name or "unknown",
            "category": row.product_category_name or "unknown",
            "price": round(float(avg_price.get(row.product_id, 0)), 2),
            "stock": 100,  # valeur factice, absente d'Olist
        }
        for row in prod_subset.itertuples()
    ]

    # ---- orders (une ligne par item de commande) ----
    orders_records = [
        {
            "customer_id": row.customer_id,
            "product_id": row.product_id,
            "order_date": pd.to_datetime(row.order_purchase_timestamp),
            "quantity": 1,
            "total_amount": round(float(row.price), 2),
        }
        for row in merged.itertuples()
    ]

    # Insertion en masse (beaucoup plus rapide qu'un .add() par ligne pour ce volume)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.bulk_insert_mappings(Customer, customers_records)
    session.bulk_insert_mappings(Product, products_records)
    session.commit()
    session.bulk_insert_mappings(Order, orders_records)
    session.commit()
    session.close()

    return {
        "customers": len(customers_records),
        "products": len(products_records),
        "orders": len(orders_records),
    }