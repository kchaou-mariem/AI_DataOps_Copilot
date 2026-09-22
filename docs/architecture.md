# Architecture détaillée — AI DataOps Copilot

## Phases

| Phase | Contenu | Dossiers concernés |
|---|---|---|
| 1 | RAG + évaluation | `backend/rag/`, `backend/eval/`, `data/documents/` |
| 2 | Agent (SQL tool, RAG tool, quality tool) | `backend/agents/` |
| 3 | Automatisation n8n | `n8n/workflows/` |
| 4 | Docker Compose + CI/CD | `docker-compose.yml`, `.github/workflows/` |
| 5 (optionnel) | Monitoring | `infrastructure/monitoring/` |
| 6 (optionnel) | Cloud | à définir |

## Dataset

- Données tabulaires : dataset Olist (e-commerce, adapté) — customers, products, orders
- Documents : 4-5 PDF rédigés manuellement (procédure retour, politique livraison, règlement interne, rapport trimestriel)

## Module RAG (Phase 1)

Voir `backend/rag/ingestion.py`, `retriever.py`, `generator.py` pour le détail des fonctions à implémenter.

## Module Agent (Phase 2)

Voir `backend/agents/tools.py` et `orchestrator.py`.

## Automatisation (Phase 3)

Workflow n8n unique : nouveau fichier de ventes déposé chaque semaine → validation → chargement PostgreSQL → notification.
