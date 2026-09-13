# 📊 Analyse & Optimisation Marketing

Projet d'analyse de données visant à **segmenter les clients, analyser les comportements d'achat et optimiser les campagnes marketing** grâce à la Data Science et à l'IA.

## 🎯 Objectifs

* Explorer et nettoyer les données clients, ventes, produits et marketing
* Segmenter les clients selon leurs caractéristiques et comportements
* Profiler les différents segments et créer des personas
* Analyser les performances des campagnes marketing
* Prédire le **churn** et la **valeur client (CLV)**
* Proposer une stratégie marketing digitale personnalisée
* Développer un dashboard interactif

## 🛠️ Technologies

* **Python** : Pandas, Matplotlib, Scikit-learn
* **Machine Learning** : K-Means, PCA, Random Forest, XGBoost, Régression Logistique
* **Dashboard** : Streamlit

## 📂 Structure

```text
├── data/              # Données (raw/ = fourni par le professeur, generated/ = synthétique)
├── dashboard/
├── docs/              # Journal d'évolution par module (ex. churn.md, segmentation.md)
├── marketing/
├── models/            # Modèles entraînés et artefacts de preprocessing, par module
├── notebooks/         # Exploration et expérimentation (EDA, comparaison de modèles)
├── outputs/           # Résultats générés par les scripts, un sous-dossier par module
├── src/               # Code source des modules churn/ et segmentation/
│   ├── churn/
│   └── segmentation/
└── README.md
```

> ⚠️ **Note sur la structure** : `churn/` et `segmentation/` vivent sous
> `src/` (package Python installable via `uv`), tandis que `dashboard/`
> et `marketing/` sont pour l'instant à la racine du projet, hors `src/`.
> Les deux conventions coexistent actuellement — pas encore harmonisées
> à l'échelle du repo.

## 🚀 Pipeline

```text
Données
   ↓
Exploration & Nettoyage
   ↓
Segmentation
   ↓
Profilage des clients
   ↓
Analyse des campagnes
   ↓
Prédiction Churn / CLV
   ↓
Stratégie marketing
   ↓
Dashboard
```

## ▶️ Exécution des scripts

> ℹ️ Les instructions ci-dessous couvrent les modules `churn/` et
> `segmentation/`, qui tournent avec `uv` (environnement et dépendances
> définis dans `pyproject.toml`/`uv.lock`).

### Prédiction du churn

Le modèle doit être disponible dans `models/churn/` (déjà versionné dans
le repo — pas besoin de ré-entraîner après un clone).

```bash
uv run python src/churn/train.py     # ré-entraîne si besoin, régénère models/churn/
uv run python src/churn/predict.py   # score tous les clients
```

Le fichier est créé dans :

```text
outputs/churn/predictions.csv
```

Détail complet : [`src/churn/README.md`](src/churn/README.md)

### Segmentation des clients

Le modèle est disponible dans `models/segmentation/` (déjà versionné).

```bash
uv run python src/segmentation/train_segmentation.py     # ré-entraîne si besoin
uv run python src/segmentation/predict_segmentation.py   # scoring
```

Les données utilisées proviennent de `data/generated/`.

Détail complet : [`src/segmentation/README.md`](src/segmentation/README.md)

## 📁 Structure des sorties

Les résultats des scripts churn et segmentation sont regroupés dans
`outputs/`, avec un sous-dossier séparé par module :

```text
outputs/
├── churn/
│   └── predictions.csv
└── segmentation/
    ├── choix_k.png
    ├── churn_par_segment.png
    ├── heatmap_rfm.png
    ├── profil_segments.csv
    ├── segmentation_clients.csv
    └── segments_final.png
```

## 🗂️ Artefacts de modèle

Les modèles entraînés (churn, segmentation) sont versionnés directement
dans Git — pas régénérés à chaque clone :

```text
models/
├── churn/
│   ├── churn_model.joblib
│   ├── scaler.joblib
│   └── feature_columns.joblib
└── segmentation/
    ├── kmeans_model.joblib
    ├── scaler.joblib
    ├── log_columns.joblib
    └── quantile_edges.joblib
```

## 📦 Livrables

* Segmentation et profils clients
* Analyse des campagnes et recommandations
* Modèles prédictifs
* Dashboard interactif
* Rapport final
* Présentation orale
