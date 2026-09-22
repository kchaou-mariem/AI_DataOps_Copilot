"""
Data profiling des fichiers CSV/Excel uploadés (Phase 1 bis / utilisé aussi en Phase 2 par quality_tool).

Calcule : nb lignes, nb colonnes, % valeurs manquantes, doublons, erreurs de format
(ex. dates invalides), et un score de qualité global.
"""

# TODO : implémenter avec pandas (df.isna().mean(), df.duplicated().sum(), etc.)
