# Contexte projet — Segmentation Client & Marketing (SMD)

Projet pédagogique : segmentation client + prédiction churn/CLV + stratégie
marketing digitale + dashboard. 3 binômes, 9 modules (M1-M9).

## Mon scope (Binôme 2 — Machine Learning)

Je travaille sur M6 : modèle prédictif de churn (Random Forest / XGBoost /
Logistic Regression). Ne pas proposer de code pour M1, M5, M7-M9
(hors scope), ni pour M2/M8 (dashboard, autre binôme).

## Données — raw vs generated (important)

- `data/raw/` — dataset ORIGINAL fourni par le professeur. Volontairement
  très peu de lignes (quelques centaines d'octets par fichier). Ne jamais
  modifier, ne jamais traiter comme le dataset d'entraînement.
- `data/generated/` — dataset synthétique produit par `generate_data.py`,
  créé précisément parce que `data/raw/` avait trop peu de lignes pour
  entraîner quoi que ce soit. C'est CE dataset qu'on utilise pour le
  modeling (customers_data.csv, sales_data.csv, products_data.csv,
  marketing_data.csv + README.md décrivant le schéma).
- Ne pas régénérer ou modifier `generate_data.py` (autre binôme le maintient).

## ⚠️ Point critique sur la cible `Churn`

`Churn` = 0 si `_Behavior` == "Active", sinon 1 (colonne interne, absente
du CSV final). C'est un proxy synthétique, pas un vrai comportement observé.
Toujours vérifier une feature candidate pour fuite de données (leakage)
avant de l'inclure, en particulier tout ce qui a pu influencer `_Behavior`
en amont (ex. Total_Spent).

## Conventions

- Python, gestion de projet via uv (pyproject.toml / uv.lock)
- Type hints obligatoires sur les fonctions publiques
- Docstrings courtes (1-2 lignes), pas de commentaires qui répètent le code
- Séparer : chargement des données / preprocessing / entraînement / évaluation
- Toujours reporter au minimum : Precision, Recall, F1, ROC-AUC, matrice de confusion

## Ne pas refaire

- Ne pas toucher à `data/raw/` ni `generate_data.py`
- Ne pas proposer de dashboard (Streamlit/Power BI) — hors scope M6
