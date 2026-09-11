# Module Churn (M6)

Prédiction du risque de départ (churn) client, à partir des données
transactionnelles générées dans `data/generated/`.

## Ce que fait ce module

1. **Feature engineering** (`features.py`) — construit un jeu de features
   par client à partir de l'historique d'achats (RFM) et des données
   démographiques.
2. **Entraînement** (`train.py`) — entraîne et sauvegarde un modèle de
   classification binaire (churn / non-churn).
3. **Scoring** (`predict.py`) — applique le modèle entraîné à l'ensemble
   des clients et exporte une probabilité de churn par client.

## Fichiers

| Fichier | Rôle |
|---|---|
| `features.py` | `compute_rfm()`, `build_feature_set()`, `encode_categorical_features()` — transformations réutilisables |
| `train.py` | Pipeline d'entraînement, exécutable seul |
| `predict.py` | Pipeline de scoring, exécutable seul |

## Installation

Ce module dépend de `uv` pour la gestion de l'environnement Python.

1. **Installer `uv`** (si pas déjà fait) — voir la
   [documentation officielle](https://docs.astral.sh/uv/getting-started/installation/)
   pour ton OS.

2. **Installer les dépendances du projet**, depuis la racine du repo :

```bash
   uv sync
```

   Ça crée l'environnement virtuel et installe toutes les dépendances
   listées dans `pyproject.toml`/`uv.lock`, y compris `src/churn` comme
   package importable (`from churn.features import ...`).

## Modèle retenu

**Logistic Regression**, choisi après comparaison avec Random Forest
(performances quasi identiques, Logistic Regression retenu pour son
interprétabilité). Détail complet du raisonnement et des décisions
prises en cours de route : voir [`docs/churn.md`](../../docs/churn.md).

| Métrique (test set) | Valeur |
|---|---|
| Recall (churn) | 0.98 |
| Precision (churn) | 1.00 |
| F1 | 0.99 |
| ROC-AUC | 0.9999 |

⚠️ Score quasi parfait attribuable à la construction déterministe du
dataset synthétique — voir la limite documentée dans `docs/churn.md`
avant de le présenter comme une performance généralisable.

## Fonctionnalités

- **Détection de fuite de données (leakage)** — `Total_Spent` (fourni
  dans `customers_data.csv`) est explicitement exclu des features : il
  encode indirectement la variable cible plutôt que de la prédire.
  RFM recalculé indépendamment comme substitut légitime.
- **Features RFM** — Recency, Frequency, Monetary, calculées depuis
  `sales_data.csv` avec une date de référence unique (2025-12-31),
  évitant tout biais par client.
- **Encodage catégoriel** — one-hot sur `Gender`/`Location`, avec
  `drop_first=True` pour éviter la redondance (dummy trap).
- **Scoring en probabilité continue** — pas de seuil binaire figé à
  0.5 : `churn_probability` est exportée telle quelle, pour laisser
  la priorisation (qui cibler en premier) aux équipes marketing (M7).

## Entrées attendues

| Fichier | Colonnes requises |
|---|---|
| `data/generated/customers_data.csv` | `Customer_ID`, `Age`, `Gender`, `Location`, `Churn` |
| `data/generated/sales_data.csv` | `Customer_ID`, `Date`, `Quantity`, `Sale_Price` |

## Sortie

`outputs/churn/predictions.csv`

| Colonne | Type | Description |
|---|---|---|
| `Customer_ID` | int | Identifiant client |
| `churn_probability` | float (0-1) | Probabilité de churn prédite, arrondie à 4 décimales |

Une ligne par client (1000 lignes sur le dataset actuel).

## Artefacts persistés

`train.py` sauvegarde 3 fichiers dans `models/churn/`, tous nécessaires
ensemble pour que `predict.py` fonctionne :

| Fichier | Contenu |
|---|---|
| `churn_model.joblib` | Le modèle Logistic Regression entraîné |
| `scaler.joblib` | Le `StandardScaler` ajusté sur le train set — obligatoire pour normaliser de nouvelles données de la même façon qu'à l'entraînement |
| `feature_columns.joblib` | La liste exacte des colonnes attendues après encodage, pour réaligner (`reindex`) les données avant de prédire si une catégorie (ex. une ville) est absente d'un futur lot |

⚠️ Les trois fichiers doivent rester synchronisés entre eux — ne jamais
utiliser un seul des trois sans relancer `train.py` en entier.

**Ces fichiers ne sont pas committés dans le repo** — `models/churn/`
est vide après un `git clone`. Il faut lancer `train.py` avant de
pouvoir utiliser `predict.py` (voir Exécution ci-dessous).

## Exécution

Depuis la racine du projet, après `uv sync` :

```bash
# 1. Entraîner le modèle (génère models/churn/*.joblib)
uv run python src/churn/train.py

# 2. Scorer tous les clients (génère outputs/churn/predictions.csv)
uv run python src/churn/predict.py
```

`train.py` doit être exécuté **au moins une fois** avant `predict.py` —
sans ça, `predict.py` lève une `FileNotFoundError` sur
`models/churn/churn_model.joblib`.

## Limites connues

- **Pas de bascule temporelle par client** — chaque client a un
  comportement figé sur toute sa période dans le dataset synthétique.
  Le modèle fait donc de la classification d'état actuel, pas de la
  prédiction précoce d'un futur départ.
- **Aucune validation croisée effectuée** — un seul split train/test
  (80/20, stratifié). Les métriques peuvent varier légèrement d'un
  split à l'autre, non quantifié ici.
