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

## 📋 Prérequis

* **Python 3.11+** (recommandé 3.11 ou 3.12)
* **Git** pour cloner le repository
* **uv** — gestionnaire de paquets et environnement Python ultra-rapide
* Environ **500 MB** d'espace disque libre (dépendances + données + modèles)

## 💾 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/Hajatiana650/SMD-project.git
cd SMD-project
```

### 2. Installer `uv`

`uv` est un remplacement ultra-rapide pour `pip` et `virtualenv`. Installez-le via :

#### Sur Linux / macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> Après l'installation, assurez-vous que `~/.local/bin` est dans votre `PATH` :
>
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```
>
> Vous pouvez ajouter cette ligne à votre fichier de profil shell (`~/.bashrc`, `~/.zshrc`, etc.) pour la rendre persistante.

#### Sur Windows

Téléchargez et exécutez l'installateur depuis [astral.sh/uv](https://astral.sh/uv), ou utilisez PowerShell :

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Important : Ajouter `uv` au PATH sur Windows**

Après l'installation, vous devez ajouter `uv` à votre variable d'environnement `PATH` :

**Option 1 : Via l'interface graphique (recommandée)**

1. Appuyez sur `Win + R`, tapez `sysdm.cpl` et appuyez sur Entrée
2. Allez à l'onglet **Variables d'environnement** en bas à droite
3. Cliquez sur **Variables d'environnement**
4. Dans la section **Variables utilisateur**, cliquez sur **Nouveau...** (ou modifiez `PATH` s'il existe)
5. Nom de la variable : `PATH`
6. Valeur : `%USERPROFILE%\AppData\Local\uv\bin`
7. Cliquez sur **OK** et fermez les fenêtres
8. **Redémarrez votre PowerShell/CMD** pour que les changements prennent effet

**Option 2 : Via PowerShell (ligne de commande)**

Exécutez en tant qu'administrateur :

```powershell
[Environment]::SetEnvironmentVariable(
    "PATH",
    "$env:PATH;$env:USERPROFILE\AppData\Local\uv\bin",
    "User"
)
```

Puis **redémarrez votre terminal**.

**Vérifier que `uv` est dans le PATH**

Ouvrez un **nouveau terminal** (PowerShell ou CMD) et exécutez :

```powershell
uv --version
```

Si vous voyez un numéro de version (ex. `uv 0.4.0`), l'installation est réussie ! ✅

#### Vérifier l'installation

```bash
uv --version
```

### 3. Installer les dépendances du projet

Une fois `uv` installé et dans votre `PATH`, exécutez :

```bash
uv sync
```

Cette commande :

* Crée un environnement virtuel isolé (`.venv/`)
* Installe toutes les dépendances déclarées dans `pyproject.toml`
* Génère/synchronise le fichier de verrous `uv.lock` pour la reproductibilité

### 4. Vérifier l'installation

```bash
uv run python --version
```

Devrait afficher Python 3.11+ depuis l'environnement virtuel du projet.

## 📂 Structure

```text
├── data/              # Données (raw/ = fourni par le professeur, generated/ = synthétique)
├── src/
│   ├── dashboard/
│   ├── marketing/
│   ├── churn/
│   └── segmentation/
├── docs/              # Journal d'évolution par module (ex. churn.md, segmentation.md)
├── models/            # Modèles entraînés et artefacts de preprocessing, par module
├── notebooks/         # Exploration et expérimentation (EDA, comparaison de modèles)
├── outputs/           # Résultats générés par les scripts, un sous-dossier par module
└── README.md
```

> Tous les modules applicatifs (`dashboard/`, `marketing/`, `churn/` et
> `segmentation/`) sont regroupés sous `src/`. Les données, modèles et
> résultats restent à la racine afin que les chemins soient indépendants du
> module exécuté.

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

### Dashboard

```bash
uv run streamlit run src/dashboard/app.py
```

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
