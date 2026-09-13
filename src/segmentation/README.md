# Module Segmentation Client (M3, M4)

Segmentation comportementale des clients à partir de leurs données transactionnelles, basée sur une approche **RFM + K-Means**.

Le module construit les indicateurs **Recency, Frequency et Monetary**, applique des transformations reproductibles, entraîne un modèle de clustering K-Means et attribue ensuite chaque client à un segment comportemental.

L'architecture sépare l'entraînement du modèle et le scoring afin de garantir que les mêmes paramètres sont utilisés lors des différentes exécutions.

## Ce que fait ce module

1. **Feature engineering RFM** (`rfm.py`) — construit les indicateurs Recency, Frequency et Monetary à partir de l'historique des ventes.
2. **Entraînement** (`train_segmentation.py`) — calcule les bornes de quantiles, ajuste les transformations, entraîne K-Means et sauvegarde les artefacts du modèle.
3. **Scoring** (`predict_segmentation.py`) — recharge les artefacts entraînés et les applique aux clients sans recalculer les paramètres.

L'architecture suit le même principe que le module Churn : une étape qui apprend les paramètres et les sauvegarde, une étape séparée qui les réutilise tels quels. Le détail des deux flux est donné plus bas dans "Principe entraînement vs scoring".

## Fichiers

| Fichier | Rôle |
| ------- | ---- |
| `rfm.py` | Fonctions réutilisables pour construire les données RFM |
| `train_segmentation.py` | Pipeline d'entraînement et de persistance des artefacts |
| `predict_segmentation.py` | Pipeline de scoring utilisant les artefacts sauvegardés |

## Installation

Ce module utilise `uv` pour la gestion de l'environnement Python.

Depuis la racine du projet :

```bash
uv sync
```

Cette commande crée l'environnement virtuel et installe les dépendances définies dans `pyproject.toml` / `uv.lock`.

## Méthode de segmentation

La segmentation repose sur les trois indicateurs RFM :

| Indicateur | Signification | Interprétation |
| ---------- | ------------- | -------------- |
| **Recency** | Nombre de jours depuis le dernier achat | Plus faible = client plus récemment actif |
| **Frequency** | Nombre d'achats effectués | Plus élevé = client plus régulier |
| **Monetary** | Montant total dépensé | Plus élevé = client à plus forte valeur |

Les valeurs RFM sont transformées en scores à l'aide de bornes de quantiles calculées pendant l'entraînement.
Les bornes calculées sont sauvegardées afin d'être réutilisées exactement de la même manière pendant le scoring.

### Calcul des quantiles

Les bornes de quantiles sont calculées directement sur les valeurs RFM originales.
Elles ne sont pas recalculées pendant le scoring.

Cette distinction est importante : si les bornes étaient recalculées sur une population différente, la définition des scores RFM pourrait changer d'une exécution à l'autre.

Les doublons sont gérés avec `duplicates="drop"` afin d'éviter qu'un grand nombre de valeurs identiques, notamment pour Frequency, empêche la construction des intervalles.

### Transformation logarithmique

Une transformation logarithmique est appliquée à Recency.
Cette transformation vise à réduire l'influence des valeurs extrêmes et à obtenir une distribution plus adaptée à la phase de clustering.

La liste des colonnes concernées est sauvegardée dans `log_columns.joblib` afin que le scoring applique exactement les mêmes transformations que l'entraînement.

### Normalisation

Les variables utilisées par K-Means sont standardisées avec un `StandardScaler`.
Le scaler est ajusté uniquement pendant l'entraînement puis sauvegardé dans :
`models/segmentation/scaler.joblib`

Lors du scoring, le même scaler est rechargé et utilisé avec `transform()`.

### Clustering K-Means

Le modèle retenu utilise :

```text
K = 3
```

Le choix du nombre de clusters est basé sur l'analyse de plusieurs métriques de clustering :

* Silhouette Score
* Calinski-Harabasz Index
* Davies-Bouldin Index

Le nombre de clusters retenu est ensuite utilisé pour entraîner le modèle K-Means final.
Le modèle entraîné est sauvegardé dans :
`models/segmentation/kmeans_model.joblib`

## Segments métier

K-Means produit initialement des clusters numériques.
Les clusters sont ensuite interprétés à partir de leurs caractéristiques RFM afin de leur attribuer une signification métier.

Les segments actuellement utilisés sont :

| Segment | Interprétation |
| ------- | -------------- |
| **VIP / Champions** | Clients présentant une forte valeur et/ou une forte activité |
| **Clients fidèles** | Clients réguliers présentant une bonne activité |
| **Occasionnels** | Clients ayant une activité intermédiaire |
| **À risque** | Clients présentant des signes d'inactivité ou de baisse d'activité |
| **Perdus** | Clients présentant une forte inactivité |
| **Nouveaux / à activer** | Clients avec peu d'historique nécessitant une activation |

> ⚠️ **Note :** K-Means ne connaît pas directement ces notions métier. Il identifie uniquement des groupes de clients ayant des caractéristiques similaires. Les noms des segments constituent donc une interprétation métier des clusters et doivent être validés en analysant les statistiques RFM de chaque groupe.

## Résultat actuel

Sur le jeu de données synthétique actuel de 1 000 clients, le scoring produit la répartition suivante :

| Segment | Nombre de clients | Pourcentage |
| ------- | ----------------- | ----------- |
| **Perdus** | 365 | 36,5 % |
| **Occasionnels** | 257 | 25,7 % |
| **VIP / Champions** | 246 | 24,6 % |
| **Clients fidèles** | 118 | 11,8 % |
| **À risque** | 13 | 1,3 % |
| **Nouveaux / à activer** | 1 | 0,1 % |
| **Total** | **1000** | **100 %** |

Cette distribution décrit uniquement le jeu de données synthétique actuellement utilisé.
Elle ne doit pas être interprétée comme une représentation générale d'une population réelle de clients.

## Entrées attendues

Les données utilisées par le module sont générées dans :
`data/generated/`

### Données transactionnelles

| Fichier | Colonnes requises |
| ------- | ----------------- |
| `data/generated/sales_data.csv` | `Customer_ID`, `Date`, `Quantity`, `Sale_Price` |
| `data/generated/customers_data.csv` | `Customer_ID` et informations client disponibles |

Les indicateurs RFM sont calculés à partir de l'historique des ventes.
La date de référence utilisée pour calculer Recency doit rester cohérente entre l'entraînement et le scoring.

## Sorties

Le scoring produit les résultats dans :
`outputs/segmentation/`

Les sorties actuelles comprennent notamment :

| Fichier | Description |
| ------- | ----------- |
| `segmentation_clients.csv` | Segmentation finale attribuée à chaque client |
| `profil_segments.csv` | Profil RFM des différents segments |
| `churn_par_segment.png` | Analyse du churn par segment |
| `heatmap_rfm.png` | Visualisation des caractéristiques RFM |
| `segments_final.png` | Visualisation finale des segments |

Une ligne de `segmentation_clients.csv` correspond à un client.

## Artefacts persistés

Les artefacts entraînés sont stockés dans :
`models/segmentation/`

| Fichier | Contenu |
| ------- | ------- |
| `scaler.joblib` | `StandardScaler` ajusté sur les données d'entraînement |
| `kmeans_model.joblib` | Modèle K-Means entraîné |
| `log_columns.joblib` | Colonnes auxquelles appliquer la transformation logarithmique |
| `quantile_edges.joblib` | Bornes de quantiles utilisées pour transformer les valeurs RFM |

### Versionnement des modèles

Contrairement à une approche où les modèles sont régénérés après chaque clone du repository, les artefacts entraînés sont versionnés dans Git.
L'objectif est de permettre aux autres membres du projet d'utiliser directement le modèle existant sans devoir relancer l'entraînement.

Après un clone du repository, les fichiers nécessaires au scoring sont donc déjà disponibles dans :
`models/segmentation/`

Les quatre artefacts doivent cependant rester synchronisés. Il ne faut pas remplacer ou régénérer un seul fichier indépendamment des autres.

Toute modification concernant :

* le calcul RFM ;
* les transformations ;
* les bornes de quantiles ;
* le scaler ;
* le nombre de clusters ;
* le modèle K-Means ;

doit être suivie d'un nouvel entraînement complet afin de régénérer l'ensemble des artefacts.

## Exécution

Depuis la racine du projet :

### 1. Entraîner le modèle

```bash
uv run python src/segmentation/train_segmentation.py
```

Cette étape :

* charge les données ;
* construit les données RFM ;
* calcule les bornes de quantiles ;
* définit les transformations ;
* ajuste le `StandardScaler` ;
* entraîne K-Means ;
* sauvegarde les quatre artefacts dans `models/segmentation/`.

### 2. Scorer les clients

```bash
uv run python src/segmentation/predict_segmentation.py
```

Cette étape :

* charge les données à scorer ;
* reconstruit les données RFM ;
* recharge les bornes de quantiles ;
* applique les transformations sauvegardées ;
* recharge le scaler ;
* recharge le modèle K-Means ;
* attribue un segment à chaque client ;
* sauvegarde les résultats dans `outputs/segmentation/`.

> ⚠️ `predict_segmentation.py` nécessite que les quatre artefacts présents dans `models/segmentation/` existent et correspondent au pipeline utilisé.

## Principe entraînement vs scoring

Le module sépare volontairement les opérations qui apprennent des paramètres de celles qui appliquent des paramètres existants.

### Pendant l'entraînement

```text
Données
   │
   ▼
Calcul RFM
   │
   ▼
Bornes de quantiles ─────────┐
   │                         │
   ▼                         │
Transformation log           │
   │                         │
   ▼                         │
StandardScaler ──────────────┤
   │                         │
   ▼                         │
K-Means ─────────────────────┤
                             │
                             ▼
                    Artefacts persistés
```

### Pendant le scoring

```text
Nouvelles données
       │
       ▼
   Calcul RFM
       │
       ▼
Bornes sauvegardées
       │
       ▼
Transformation log
       │
       ▼
Scaler sauvegardé
       │
       ▼
K-Means sauvegardé
       │
       ▼
Segmentation
```

Le scoring ne doit donc jamais réapprendre les paramètres du modèle. Cela permet de conserver une définition stable des segments lorsque la population à scorer change.

## Problème de conception corrigé

Une première version du module recalculait entièrement :

* les bornes de quantiles ;
* le scaler ;
* le clustering K-Means ;

à chaque exécution.

Cette approche pouvait provoquer une incohérence. Par exemple, si la population de clients changeait, les bornes de `qcut` pouvaient changer et les centroïdes K-Means pouvaient être différents. Un même client pouvait alors recevoir un segment différent alors que son propre comportement n'avait pas changé.

Le module a donc été refactorisé selon le même principe que le module Churn : une étape d'entraînement qui apprend les paramètres et les sauvegarde, une étape de scoring qui les réutilise sans les recalculer (voir "Principe entraînement vs scoring" ci-dessus pour le détail des deux flux).

Un second problème a été identifié pendant l'implémentation : les bornes de quantiles étaient initialement calculées sur le **rang** des valeurs (`.rank()`, utile pour gérer les ex-æquo) plutôt que sur les valeurs RFM brutes. Le scoring appliquait ensuite ces bornes directement aux valeurs brutes — un décalage d'échelle qui faisait tomber la plupart des clients hors des tranches attendues. Corrigé en calculant les bornes directement sur les valeurs RFM, avec `duplicates="drop"` pour gérer les cas où trop de valeurs identiques (notamment Frequency) empêchent 5 tranches distinctes. Détail complet : voir `docs/segmentation.md`.

## Validation du résultat

Une vérification manuelle a été effectuée (voir `notebooks/segmentation_validation.ipynb` et l'entrée correspondante dans `docs/segmentation.md`), en deux temps :

1. **Inspection du seul client classé "Nouveaux / à activer"** (Customer_ID 2634) — profil confirmé cohérent avec la règle de `label_from_rfm` (achat récent, mais peu fréquent et peu dépensier). Pas un bug, juste un segment naturellement rare dans ce dataset.
2. **Taux de churn par segment**, pour vérifier que les noms attribués aux clusters correspondent à un vrai comportement :

| Segment | Taux de churn | Clients |
|---|---|---|
| Perdus | 100% | 365 |
| À risque | 76.9% | 13 |
| Occasionnels | 12.8% | 257 |
| VIP / Champions | 0% | 246 |
| Clients fidèles | 0% | 118 |
| Nouveaux / à activer | 0% | 1 |

La cohérence est quasi parfaite avec les noms des segments — mais cette cohérence doit être nuancée, voir "Limites connues" ci-dessous : elle ne constitue pas une preuve indépendante de la qualité du clustering.

## Limites connues

* **Données synthétiques :** Les données utilisées actuellement sont synthétiques. Les résultats obtenus ne permettent donc pas de conclure que la segmentation aura la même pertinence sur de véritables données clients.
* **RFM et Churn partagent la même origine, pas deux signaux indépendants :** dans `generate_data.py`, `_Behavior` détermine à la fois la cible `Churn` et les leviers qui construisent le RFM (nombre d'achats, quantité, accès aux produits premium — voir `docs/churn.md`). La cohérence quasi parfaite entre segments et taux de churn (100%/0%) reflète donc en grande partie cette origine commune, pas une validation indépendante que la segmentation "prédit" le churn. À présenter comme telle dans le rapport final (M9), pas comme une performance généralisable.
* **Choix de K :** K-Means nécessite de choisir le nombre de clusters. Le modèle actuel utilise $K = 3$, déterminé à partir de plusieurs métriques de clustering. Le détail des scores obtenus pour les différentes valeurs de K doit être conservé dans la documentation du projet afin de justifier ce choix dans le rapport final.
* **Sensibilité aux données :** Les résultats d'un clustering dépendent des données utilisées lors de l'entraînement. Si les données deviennent très différentes du dataset actuel, une réévaluation du modèle et de ses segments peut être nécessaire.
* **Absence de prédiction temporelle :** La segmentation décrit le comportement observé sur la période disponible. Elle ne prédit pas directement l'évolution future du client. Pour estimer le risque de départ futur, le module Churn est utilisé en complément.

## Relation avec le module Churn

La segmentation et le modèle Churn répondent à deux questions différentes.

### Segmentation

Quel type de comportement présente actuellement ce client ?

```text
Client ──► RFM ──► K-Means ──► Segment
```

### Churn

Quelle est la probabilité que ce client soit associé au churn ?

```text
Client ──► Features ──► Logistic Regression ──► churn_probability
```

Les deux informations sont complémentaires. Par exemple :

```text
VIP / Champions
        +
forte probabilité de churn
        │
        ▼
Client à forte valeur présentant un risque élevé
        │
        ▼
Priorité élevée pour une action de rétention
```

La segmentation fournit donc une vue comportementale du client, tandis que le modèle Churn fournit une estimation du risque de départ. Ces deux résultats peuvent ensuite être exploités par le module marketing pour définir et prioriser les actions commerciales.
