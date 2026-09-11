# Journal d'évolution — Dashboard (M8)

> Historique des décisions techniques du module M8 (Binôme 1 — Data Engineering & Dashboard).

---

## 10 septembre 2026 — Choix de la technologie

**Ce qui a changé / a été décidé**

Choix de **Streamlit** pour développer le dashboard interactif, avec **Plotly** pour les visualisations.

**Pourquoi**

Streamlit permet de construire rapidement une application interactive en Python et facilite l'intégration avec les données Pandas et les futurs résultats ML.

---

## 10 septembre 2026 — Mise en place de l'architecture

**Ce qui a changé / a été décidé**

Création du dossier `dashboard/` avec une séparation entre l'application, les pages et les fonctions utilitaires.

Structure prévue :

`dashboard/app.py`
`dashboard/pages/`
`dashboard/components/`
`dashboard/utils/`

**Pourquoi**

Préparer une architecture permettant d'intégrer progressivement les résultats des modules M2 à M7 sans devoir reconstruire le dashboard.

---

## 10 septembre 2026 — Chargement centralisé des données

**Ce qui a changé / a été décidé**

Création de `dashboard/utils/data_loader.py` pour charger les fichiers présents dans `data/processed/`.

**Données chargées**

- `customers_data.csv`
- `sales_data.csv`
- `products_data.csv`
- `marketing_data.csv`
- `customer_analytics.csv`

**Pourquoi**

Centraliser l'accès aux données et éviter de répéter le code de chargement dans chaque page.

---

## 10 septembre 2026 — Première version du dashboard

**Ce qui a changé / a été décidé**

Création de `dashboard/app.py` avec une première vue globale et des KPI.

**KPI prévus**

- nombre de clients ;
- nombre de ventes ;
- nombre de produits ;
- nombre de campagnes ;
- chiffre d'affaires.

**Résultat**

Le dashboard peut fonctionner avec les données M2 sans attendre les résultats ML de B2.

---

## 10 septembre 2026 — Premières visualisations

**Ce qui a changé / a été décidé**

Préparation de visualisations du chiffre d'affaires par catégorie et par marque avec Plotly.

**Pourquoi**

Commencer le développement du dashboard indépendamment des modules de segmentation, churn et CLV.

**Prochaine étape**

Créer les pages `Overview`, `Customers`, `Segmentation`, `Churn_CLV` et `Marketing`, puis ajouter progressivement les résultats fournis par B2.
