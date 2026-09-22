"""
Modèles SQLAlchemy pour les tables retail : customers, products, orders.
Schéma basé sur le dataset Olist (adapté).
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# TODO : définir Customer, Product, Order (colonnes détaillées dans docs/architecture.md)
