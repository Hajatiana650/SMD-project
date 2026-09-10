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

## 10 septembre 2026 — Confirmation du leakage sur Total_Spent

**Ce qui a changé / a été décidé**
Analyse du code de `generate_data.py` (section 4) : `Total_Spent` exclu
définitivement des features candidates pour M6.

**Pourquoi**
`_Behavior` détermine directement `purchase_count`, `quantity_max` et l'accès
aux produits premium — les 3 leviers qui construisent `Total_Spent`. De plus,
`Total_Spent` agrège toute la période sans coupure temporelle : c'est un
résumé rétrospectif du comportement déjà connu, pas un signal prédictif.

**Résultat**
Écart moyen ×6 entre churners et non-churners (8450 vs 1352) confirmé comme
artefact de génération, pas comme signal métier légitime.

---

## 10 septembre 2026 — Clarification leakage vs signal légitime

**Décision** : Total_Spent (customers_data.csv) reste exclu — origine/fenêtre
inconnue. RFM calculé nous-mêmes (Recency/Frequency/Monetary depuis
sales_data.csv) retenu comme feature set principal pour M6, conformément à
l'usage prévu par generate_data.py.

**Limite notée** : dataset sans bascule temporelle par client → modèle de
classification d'état, pas de prédiction précoce. Détail : voir eda_churn.ipynb.

---

## 10 septembre 2026 — Baseline Logistic Regression entraîné

**Ce qui a changé / a été décidé**
Premier modèle entraîné : Logistic Regression sur RFM + Age + Gender +
Location (16 features encodées), split 80/20 stratifié.

**Résultat**
Recall 0.98, Precision 1.00, F1 0.99, ROC-AUC 0.9999 — 2 faux négatifs
sur 200. Coefficients dominants : Monetary (-3.96), Recency (+3.36),
cohérents avec l'intuition métier (RFM). Détail complet et lecture des
coefficients : voir notebooks/model_training.ipynb.

**Limite à retenir pour M9**
Score quasi parfait attribué à la construction déterministe du dataset
synthétique (Recency/Frequency/Monetary séparent déjà les classes
presque sans chevauchement dès l'EDA), pas à une performance
généralisable en conditions réelles. À présenter comme limite du
dataset, pas comme preuve de qualité du modèle.

---

## 10 septembre 2026 — Séparation eda_churn / model_training

**Décision**
`eda_churn.ipynb` reste limité à l'exploration et la validation du feature
set (déjà clôturé par une cellule de conclusion). La comparaison de
modèles part dans un nouveau notebook, `notebooks/model_training.ipynb`,
qui réutilise `build_feature_set()`/`encode_categorical_features()` depuis
`src/churn/features.py` plutôt que de recopier la logique.

---

## 10 septembre 2026 — Random Forest comparé, Logistic Regression retenu

**Résultat**
Random Forest entraîné (n_estimators=200, max_depth=10) : Recall 0.98,
Precision 1.00, ROC-AUC 0.9998 — quasi identique à Logistic Regression
(0.98/1.00/0.9999). Feature importance confirme la même hiérarchie que
les coefficients LR (Monetary > Recency > Frequency >> démographie),
validant le signal RFM par deux méthodes indépendantes.

**Décision**
Logistic Regression retenu comme modèle final pour M6 : performance
identique, mais plus interprétable (coefficients directs) et plus
simple à défendre à l'oral (M9) que Random Forest.

**Cas limite noté**
Un client (Recency élevée mais Frequency/Monetary de profil non-churn)
rate par les deux modèles — profil hybride réaliste, pas une anomalie
du dataset. Détail : notebooks/model_training.ipynb.

---
