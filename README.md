# AI DataOps Copilot

Plateforme intelligente permettant à une entreprise (retail / e-commerce) de :
- centraliser et nettoyer ses données de vente (Data Engineering)
- interroger ses documents internes via RAG (procédures, politiques, rapports)
- poser des questions en langage naturel via un agent IA qui choisit le bon outil (SQL, RAG, qualité des données)
- automatiser ses tâches récurrentes avec n8n
- tourner en conteneurs avec une pipeline CI/CD

## Statut du projet

- [ ] Phase 1 — RAG + évaluation
- [ ] Phase 2 — Agent IA (SQL tool, RAG tool, data quality tool)
- [ ] Phase 3 — Automatisation n8n
- [ ] Phase 4 — Docker Compose + CI/CD
- [ ] Phase 5 (optionnel) — Monitoring (Prometheus/Grafana)
- [ ] Phase 6 (optionnel) — Déploiement cloud

## Architecture

```
                         UTILISATEUR (entreprise)
                                  │
                    ┌─────────────▼─────────────┐
                    │      Frontend (React)      │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      FastAPI (Backend)     │
                    └─────────────┬─────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
  DATA PIPELINE              AGENT + RAG                  n8n
        │                         │                         │
        ▼                    ┌────┴────┐                    │
   PostgreSQL          SQL tool   RAG tool                   │
                            │         │                        │
                            │      Qdrant                      │
                            │         │                        │
                            │      Ollama/LLM                  │
                            └────┬────┘                        │
                              Réponse + Sources ◄───────────────┘
```

## Stack technique

| Composant | Choix |
|---|---|
| Backend API | FastAPI |
| Base de données | PostgreSQL |
| Vector store | Qdrant |
| LLM | Ollama (local) |
| Embeddings | sentence-transformers (bge-small) |
| Extraction PDF | pdfplumber |
| Évaluation RAG | RAGAS |
| Automatisation | n8n |
| Conteneurisation | Docker Compose |
| CI/CD | GitHub Actions |

## Installation

```bash
cp .env.example .env
docker-compose up -d
```

L'API sera disponible sur `http://localhost:8000/docs`.

## Structure du projet

Voir `docs/architecture.md` pour le détail de chaque module.

## Évaluation RAG

Résultats du dernier run d'évaluation (`backend/eval/evaluate.py`) :

```
(à compléter après la Phase 1)
Faithfulness:        —
Retrieval precision: —
```
