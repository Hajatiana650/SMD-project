# Journal d'évolution — Data Preparation (M2)

> Historique des décisions techniques du module M2 (Binôme 1 — Data Engineering & Dashboard).

---

## Septembre 2026 — Audit des données

**Ce qui a changé / a été décidé**

Audit des quatre tables disponibles : `customers_data.csv`, `sales_data.csv`, `products_data.csv` et `marketing_data.csv`.

**Vérifications effectuées**

- colonnes et types de données ;
- valeurs manquantes ;
- doublons ;
- clés primaires et étrangères ;
- cohérence des relations entre les tables ;
- cohérence des dates et des valeurs numériques.

**Résultat**

Les relations principales ont été validées :

- `Customer_ID` relie les clients aux ventes ;
- `Product_ID` relie les produits aux ventes ;
- les données marketing sont analysées principalement par `Channel`.

---

## Septembre 2026 — Nettoyage et préparation

**Ce qui a changé / a été décidé**

Nettoyage des données et conversion des colonnes de dates avec Pandas. Création d'une jointure entre ventes, produits et clients afin de produire des informations agrégées au niveau client.

**Pourquoi**

Fournir à B2 des données directement exploitables pour la segmentation, le churn et la CLV.

**Résultat**

Création de `customer_analytics.csv` contenant notamment :

`Customer_ID`, `Number_Of_Purchases`, `Total_Quantity`, `Sales_Revenue`, `Average_Purchase`, `Age`, `Gender`, `Location`, `Join_Date` et `Total_Spent`.

---

## Septembre 2026 — Génération de données

**Ce qui a changé / a été décidé**

Utilisation d'un dataset synthétique augmenté afin de disposer d'un volume suffisant pour les analyses et les modèles ML.

**Pourquoi**

Le dataset initial était trop petit pour permettre des analyses représentatives et un entraînement ML intéressant.

**Résultat**

Les données générées conservent le schéma des quatre tables originales et respectent les relations entre clients, ventes et produits.
