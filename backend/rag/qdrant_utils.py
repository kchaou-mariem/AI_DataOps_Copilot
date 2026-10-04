"""
Utilitaire de connexion Qdrant — gère aussi bien Qdrant local (Docker)
que Qdrant Cloud (HTTPS + clé API), selon les variables d'environnement.
"""
import os
from qdrant_client import QdrantClient


def get_qdrant_client() -> QdrantClient:
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", 6333))
    api_key = os.getenv("QDRANT_API_KEY")  # absent en local, présent en cloud
    use_https = os.getenv("QDRANT_USE_HTTPS", "false").lower() == "true"

    if api_key:
        # Qdrant Cloud : connexion via URL complète + clé API
        scheme = "https" if use_https else "http"
        url = f"{scheme}://{host}"
        return QdrantClient(url=url, api_key=api_key)

    # Qdrant local (Docker) : connexion simple host/port, sans clé
    return QdrantClient(host=host, port=port)

# Quel .env est chargé ?
#         │
#         ├─ .env (local, pas de clé)
#         │       → api_key = None
#         │       → connexion locale (localhost:6333)
#         │
#         └─ .env.cloud (contient QDRANT_API_KEY)
#                 → api_key = "ta-clé-secrète"
#                 → connexion Qdrant Cloud (HTTPS + authentification)