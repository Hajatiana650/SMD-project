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
* **R** : dplyr, ggplot2
* **Dashboard** : Streamlit / Power BI / Tableau

## 📂 Structure

```text
├── data/          # Données (raw/ = fourni par le professeur, generated/ = synthétique)
├── docs/          # Journal d'évolution par module (ex. churn.md)
├── models/        # Modèles entraînés et artefacts de preprocessing, par module
├── notebooks/     # Exploration et expérimentation (EDA, comparaison de modèles)
├── outputs/       # Résultats générés par les scripts, un sous-dossier par module
├── src/           # Code source des modules (churn/, segmentation/)
└── README.md
```

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

Les scripts doivent être lancés depuis la racine du projet avec `uv`.
L'environnement et les dépendances sont définis dans `pyproject.toml` et
`uv.lock`.

### Prédiction du churn

Le modèle doit être disponible dans `models/churn/`. Pour générer les
probabilités de churn pour tous les clients :

```bash
uv run python src/churn/predict.py
```

Le fichier est créé dans :

```text
outputs/churn/predictions.csv
```

### Segmentation des clients

Pour exécuter le calcul RFM, le clustering K-Means et générer les profils :

```bash
uv run python src/segmentation/client_segmentation.py
```

Les données utilisées proviennent de `data/generated/`.

## 📁 Structure des sorties

Les résultats des deux scripts sont regroupés dans `outputs/`, avec un
sous-dossier séparé pour chaque module :

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

## 📦 Livrables

* Segmentation et profils clients
* Analyse des campagnes et recommandations
* Modèles prédictifs
* Dashboard interactif
* Rapport final
* Présentation orale
