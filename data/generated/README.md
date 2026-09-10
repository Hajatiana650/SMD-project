# 📘 Documentation — Générateur de Données Synthétiques

> Projet pédagogique : **Analyse & Optimisation Marketing basée sur la Segmentation Client**
> Fichier documenté : `generate_data.py`
> Version : 1.0
> Date : Septembre 2026

---

## 📑 Table des matières

1. [Objectif du script](#1-objectif-du-script)
2. [Vue d'ensemble des fichiers générés](#2-vue-densemble-des-fichiers-générés)
3. [Architecture du script (10 sections)](#3-architecture-du-script-10-sections)
4. [Règles de cohérence garanties](#4-règles-de-cohérence-garanties)
5. [🔴 La colonne `Churn` — Définition et limites](#5--la-colonne-churn--définition-et-limites)
6. [Le lien `Sales.Campaign_ID` ↔ `Marketing.Campaign_ID`](#6-le-lien-salescampaign_id--marketingcampaign_id)
7. [Couverture des modules du projet](#7-couverture-des-modules-du-projet)
8. [Contrôles qualité automatiques](#8-contrôles-qualité-automatiques)
9. [Comment exécuter le script](#9-comment-exécuter-le-script)
10. [Limites connues et améliorations possibles](#10-limites-connues-et-améliorations-possibles)

---

## 1. Objectif du script

Le script `generate_data.py` génère **un jeu de données synthétique réaliste et cohérent** simulant l'activité d'un e-commerce, afin d'alimenter les 9 modules pédagogiques du projet.

Il produit **4 fichiers CSV** + **1 dictionnaire de données** (`data_dictionary.md`), tous exploitables immédiatement par les trois binômes :
- **Binôme 1** (Data Engineering & Dashboard) → exploration et dashboard.
- **Binôme 2** (Machine Learning) → segmentation, churn, CLV.
- **Binôme 3** (Marketing & Stratégie) → analyse des campagnes et personas.

---

## 2. Vue d'ensemble des fichiers générés

Tous les fichiers sont écrits dans `data/generated/`.

| Fichier | Lignes | Description |
| :--- | :--- | :--- |
| `customers_data.csv` | 1 000 | Profils clients + `Total_Spent` + `Churn` |
| `products_data.csv` | 100 | Catalogue produits (4 catégories, 10 marques) |
| `sales_data.csv` | ~15 000 | Transactions (100 % rattachées à une campagne) |
| `marketing_data.csv` | ~325 | Campagnes marketing (couverture continue par canal) |
| `data_dictionary.md` | — | Dictionnaire des données auto-généré (Data Contract V1) |

---

## 3. Architecture du script (10 sections)

Le script est découpé en **10 sections numérotées et commentées** :

| Section | Contenu |
| :--- | :--- |
| **0. En-tête** | Docstring décrivant l'objectif, les fichiers produits, les règles de cohérence |
| **1. Imports** | `random`, `datetime`, `pathlib`, `numpy`, `pandas`, `faker` |
| **2. Configuration globale** | Seeds (42), volumes, dates, dossier de sortie |
| **3. Produits** | 100 produits répartis dans 4 catégories avec prix réalistes |
| **4. Clients** | 1 000 clients avec un comportement interne (`Active`/`At Risk`/`Churned`) |
| **5. Campagnes marketing** | Couverture continue par canal (chevauchement garanti) |
| **6. Ventes** | Achats générés selon le comportement, avec attribution systématique de `Campaign_ID` |
| **7. Total_Spent** | Calcul exact : `sum(Quantity × Sale_Price)` par client |
| **8. Fusion + Churn** | Fusion clients/spending + création de la cible `Churn` |
| **9. Export CSV + dictionnaire** | Écriture des 4 CSV + `data_dictionary.md` |
| **10. Contrôles qualité** | 8 vérifications automatiques + statistiques clés |

---

## 4. Règles de cohérence garanties

Le script garantit **8 règles de cohérence** vérifiables automatiquement :

| # | Règle |
| :--- | :--- |
| 1 | Aucun achat avant la date d'inscription du client |
| 2 | `Sale_Price` = prix **unitaire** du produit (pas le total de la ligne) |
| 3 | `Total_Spent` = somme exacte des `Quantity × Sale_Price` du client |
| 4 | `Impressions ≥ Clics ≥ Conversions` pour chaque campagne |
| 5 | `End_Date > Start_Date` pour chaque campagne |
| 6 | **100 %** des ventes ont un `Campaign_ID` valide |
| 7 | La date d'achat est toujours dans `[Start_Date, End_Date]` de sa campagne |
| 8 | Le canal de la vente == le canal de la campagne attribuée |

---

## 5. 🔴 La colonne `Churn` — Définition et limites

Cette section est **la plus importante** de la documentation, car la définition du churn est **un choix de conception** qui impacte directement le module M6.

### 5.1. Pourquoi une colonne `Churn` ?

Le module **M6** du projet demande :

> *"Modèles prédictifs sur la fidélité ou la valeur client. Random Forest, XGBoost, Logistic Regression."*

Pour entraîner un modèle **supervisé**, il faut une **variable cible `y`**. Sans colonne `Churn`, le Binôme 2 ne peut pas entraîner de modèle de classification. La colonne a donc été ajoutée pour rendre le dataset **directement exploitable**.

### 5.2. Définition actuelle (dans le script)

La cible `Churn` est dérivée de la colonne interne `_Behavior` :

```python
customers["Churn"] = customers["_Behavior"].apply(
    lambda b: 0 if b == "Active" else 1
)