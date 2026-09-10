# 📊 Documentation — Dashboard Marketing Analytics

> Binôme 1 — Dashboard Streamlit | Version V0 | Septembre 2026

---

## 🏗️ Architecture
dashboard/
├── app.py ← Page d'accueil
├── utils/data_loader.py ← Charge les 5 CSV
└── pages/
    ├── Overview.py ← Vue globale
    ├── Clients.py ← Analyse clients
    ├── Produits.py ← Analyse produits
    ├── Marketing.py ← Analyse campagnes
    └── Nouveau_produit.py ← Opportunités (en cours)


Streamlit transforme automatiquement chaque fichier dans `pages/` en page de la sidebar.

---

## 📄 app.py — Page d'accueil

| Élément | Type | Description |
| :--- | :--- | :--- |
| 5 compteurs | `st.metric` | Nombre de clients, ventes, produits, campagnes, lignes analytics |

**Utilité** : vue d'ensemble instantanée des volumes de données disponibles.

---

## 📄 Overview.py — Vue globale

| Visualisation | Type | Ce qu'elle montre | Public |
| :--- | :--- | :--- | :--- |
| 4 KPIs | `st.metric` | CA total, nb ventes, panier moyen, quantité vendue | Tous |
| Taux de churn | `st.metric` | % clients churnés + fraction | B2, B3 |
| Évolution CA mensuel | Line chart | Tendance du CA dans le temps | B3 |
| Ventes par canal | Bar chart | Volume de transactions par canal | B3 |
| CA par catégorie | Bar chart | Catégorie la plus rentable | B3 |
| CA par marque | Bar chart | Marque la plus rentable | B3 |
| CA par canal | Camembert | Répartition du CA par canal | B3 |
| Tableau ventes | `st.dataframe` | Données brutes filtrées | Tous |

**Filtre** : sélection du canal (Online, In-Store, Social, Email, TV).

---

## 📄 Clients.py — Analyse démographique

| Visualisation | Type | Ce qu'elle montre | Public |
| :--- | :--- | :--- | :--- |
| 4 KPIs | `st.metric` | Nb clients, âge moyen, taux churn, CA moyen/client | Tous |
| Distribution âge | Histogramme | Répartition des clients par tranche d'âge | B2, B3 |
| Répartition genre | Camembert | % Hommes / Femmes | B3 |
| Clients par ville | Bar chart horizontal | Villes les plus représentées | B3 |
| Churn (Actif/Churné) | Camembert | Équilibre des classes | B2 |
| Dépenses selon statut | Boxplot | Distribution des dépenses Actif vs Churné | B2 |

**Filtre** : sélection du genre.

**Pourquoi ces graphiques ?**
- **B2 (ML)** : le camembert churn révèle si les classes sont équilibrées (impact sur le choix du modèle).
- **B3 (Marketing)** : le top villes aide à cibler géographiquement les campagnes.

---

## 📄 Produits.py — Analyse du catalogue

| Visualisation | Type | Ce qu'elle montre | Public |
| :--- | :--- | :--- | :--- |
| 4 KPIs | `st.metric` | Nb produits, catégories, marques, prix moyen | Tous |
| CA par catégorie | Bar chart | Catégorie la plus rentable | B3 |
| CA par marque | Bar chart | Marque la plus rentable | B3 |
| Top 10 produits | Bar chart horizontal | Best-sellers en quantité | B3 |
| Prix moyen par catégorie | Bar chart | Positionnement tarifaire | B3 |

**Filtre** : sélection de la catégorie.

**Pourquoi ces graphiques ?**
- Repérer les **best-sellers** à mettre en avant dans les campagnes.
- Comparer les **gammes de prix** entre catégories.

---

## 📄 Marketing.py — Analyse des campagnes

| Visualisation | Type | Ce qu'elle montre | Public |
| :--- | :--- | :--- | :--- |
| 4 KPIs | `st.metric` | Nb campagnes, budget, conversions, ROI moyen | B3 |
| Budget par canal | Bar chart | Où va l'argent | B3 |
| Conversions par canal | Bar chart | Canaux les plus efficaces | B3 |
| ROI moyen par canal | Bar chart | Canaux les plus rentables | B3 |
| Budget vs Revenu | Scatter plot | Corrélation budget → revenu (taille = conversions) | B3 |
| Tableau campagnes | `st.dataframe` | Détail campagne par campagne | B3 |

**Filtre** : sélection du canal.

**Pourquoi ces graphiques ?**
- Le **scatter Budget vs Revenu** montre si investir plus rapporte plus (points alignés = bonne corrélation).
- Le **ROI par canal** aide à réaffecter le budget vers les canaux rentables.

---

## 📖 Glossaire

### Termes métier

| Terme | Définition |
| :--- | :--- |
| **CA (Chiffre d'Affaires)** | Somme des ventes = `Σ (Quantity × Sale_Price)` |
| **Panier moyen** | CA total / nombre de ventes |
| **KPI** | Indicateur clé chiffré qui mesure un objectif |
| **Churn** | Client qui arrête d'acheter. `0` = actif, `1` = churné |
| **Taux de churn** | Nb churnés / Nb total clients |
| **ROI** | `(Revenu − Coût) / Coût`. Positif = rentable |
| **Taux de conversion** | `Conversions / Clics` |
| **CTR** | `Clics / Impressions` (attractivité d'une pub) |
| **Impressions** | Nb d'affichages d'une pub |
| **RFM** | Recency / Frequency / Monetary — base de la segmentation client |
| **Persona** | Profil type fictif représentant un segment |
| **CLV** | Valeur totale qu'un client génère sur sa durée de vie |

### Termes techniques

| Terme | Définition |
| :--- | :--- |
| **Streamlit** | Framework Python pour créer des apps web interactives |
| **Plotly Express** | Bibliothèque de graphiques interactifs (zoom, hover) |
| **DataFrame** | Tableau en mémoire (type Excel) de Pandas |
| **Merge** | Jointure entre 2 DataFrames sur une clé commune |
| **`Sale_Price`** | Prix **unitaire** du produit |
| **`Revenue`** | CA **de la ligne** = `Quantity × Sale_Price` |
| **`data_loader.py`** | Module centralisé qui charge les 5 CSV |
| **`st.selectbox`** | Menu déroulant interactif |

---

## ⚠️ Règles de conception

1. **Toujours calculer `Revenue = Quantity × Sale_Price`** avant toute analyse de CA. Utiliser `Sale_Price` seul sous-estime le CA d'un facteur ~2.86.
2. **Les filtres créent une copie `df_filtered`** pour ne pas modifier le DataFrame original.
3. **Chaque graphique a un titre + axes nommés**.
4. **Les tableaux bruts sont repliables** (`st.expander`).
5. **Structure identique en 10 sections** dans chaque page.

---

## 🚀 Lancement

```bash
pip install streamlit plotly pandas pyarrow
cd dashboard
streamlit run app.py