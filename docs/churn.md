# Journal d'évolution — Modèle Churn (M6)

> Historique des décisions techniques du module M6 (Binôme 2 — churn).
> Ajouter les nouvelles entrées à la fin du fichier, ne jamais réécrire l'historique existant.

---

## Septembre 2026 — Génération d'un dataset synthétique

**Ce qui a changé / a été décidé**
Création de `generate_data.py` pour produire un dataset augmenté (`data/generated/`), en complément du dataset fourni par le professeur (`data/raw/`).

**Pourquoi**
`data/raw/` contient trop peu de lignes pour entraîner un modèle exploitable. Le dataset synthétique reproduit la structure et les règles de cohérence attendues (achats cohérents avec les dates d'inscription, campagnes valides, etc.) pour permettre un travail réaliste sur les 9 modules.

**Résultat**
4 fichiers CSV générés : `customers_data.csv` (1000 lignes), `products_data.csv` (100), `sales_data.csv` (~15000), `marketing_data.csv` (~325), + `data_dictionary.md`.

---

## 10 septembre 2026 — Définition initiale de la cible Churn

**Ce qui a changé / a été décidé**
La cible `Churn` est dérivée d'un champ interne `_Behavior` (Active / At Risk / Churned), absent du CSV final : `Churn = 0` si `Active`, sinon `1`.

**Pourquoi**
Le module M6 exige une variable cible binaire pour entraîner un modèle supervisé (Random Forest / XGBoost / Logistic Regression). Cette définition rend le dataset immédiatement exploitable.

**Limite identifiée**
`Churn` est un proxy synthétique, pas un comportement observé réel. Risque de fuite de données (leakage) si une feature a influencé `_Behavior` en amont (ex. `Total_Spent`) — à vérifier avant tout entraînement.

---

## 10 septembre 2026 — Début de la conception du modèle churn

**Ce qui a changé / a été décidé**
Démarrage du travail sur la branche `feature/churn`. Mise en place du contexte projet pour l'agent Copilot (`.github/copilot-instructions.md`) et de ce journal (`docs/churn.md`).

**Pourquoi**
Garder une trace des décisions de modélisation au fil de l'eau, pour le rapport final (M9) et pour limiter la réexplication de contexte à l'agent IA.

---
