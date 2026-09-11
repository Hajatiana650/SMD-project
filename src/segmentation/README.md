# Module Segmentation Client (M3, M4)

Segmentation des clients par RFM (Recency, Frequency, Monetary) et
clustering K-Means, à partir des données transactionnelles générées
dans `data/generated/`.

## Ce que fait ce module

1. **Feature engineering** — réutilise `build_feature_set()` du module
   churn (`churn.features`) pour calculer le RFM, évitant de dupliquer
   la logique entre les deux modules.
2. **Transformation** — log-transform des colonnes RFM asymétriques,
   normalisation (`StandardScaler`).
3. **Choix du nombre de clusters** — comparaison sur plusieurs valeurs
   de K via silhouette score, Calinski-Harabasz, Davies-Bouldin.
4. **Clustering** — K-Means sur les features RFM normalisées.
5. **Scoring RFM et labellisation** — scores R/F/M par quantiles,
   segments marketing nommés (VIP, À risque, Perdus, etc.).
6. **Profilage et visualisation** — statistiques par segment, taux de
   churn par segment, graphiques (heatmap, scatter, distribution).

## Fichiers

| Fichier | Rôle |
|---|---|
| `client_segmentation.py` | Pipeline complet, exécutable seul |

## Installation

Ce module dépend de `uv`. Depuis la racine du projet :

```bash
uv sync
```

## Entrées attendues

| Fichier | Colonnes requises |
|---|---|
| `data/generated/customers_data.csv` | `Customer_ID`, `Name`, `Age`, `Gender`, `Location`, `Join_Date`, `Churn` |
| `data/generated/sales_data.csv` | `Sale_ID`, `Customer_ID`, `Date`, `Quantity`, `Sale_Price` |

## Sorties

`outputs/segmentation/`

| Fichier | Contenu |
|---|---|
| `segmentation_clients.csv` | Une ligne par client : RFM, scores, cluster, segment, recommandation marketing |
| `profil_segments.csv` | Statistiques agrégées par segment (moyennes, taux de churn, % de la base) |
| `choix_k.png` | Graphiques des 4 métriques utilisées pour choisir K |
| `segments_final.png` | Scatter Recency/Monetary, boxplot panier moyen, effectifs par segment |
| `churn_par_segment.png` | Taux de churn par segment (barplot) |
| `heatmap_rfm.png` | Profil RFM normalisé moyen par segment |

## Segments produits

| Segment | Critère RFM (scores R/F/M sur 5) |
|---|---|
| VIP / Champions | R≥4, F≥4, M≥4 |
| Clients fidèles | R≥3, F≥4, M≥3 |
| Gros panier occasionnel | M≥4, F≤2 |
| À risque | R≤2, F≥3, M≥3 |
| Nouveaux / à activer | R≥4, F≤2, M≤2 |
| Perdus | R≤2, F≤2, M≤2 |
| Occasionnels | (par défaut, aucun critère ci-dessus) |

## Exécution

Depuis la racine du projet, après `uv sync` :

```bash
uv run python src/segmentation/client_segmentation.py
```

## Limites connues

- Les seuils de segments (`label_from_rfm`) supposent exactement 5
  niveaux de score — fonctionne sur `data/generated/` (1000 clients),
  pas garanti sur un dataset plus petit (ex. `data/raw/`).
- Le modèle K-Means n'est pas persisté (pas de `.joblib`) — chaque
  exécution ré-entraîne le clustering depuis zéro plutôt que
  réutiliser un modèle sauvegardé.
- Le nombre minimal de clusters est forcé à 3, indépendamment du vote
  des métriques, pour garantir une granularité exploitable en
  stratégie marketing (M7).
