# Revue des problèmes d'exécution

## Fichiers analysés

- `src/churn/features.py`
- `src/segmentation/client_segmentation.py`

## Blocage principal

`client_segmentation.py` utilise des chemins Windows :

```python
r"..\data\processed\products_data.csv"
```

Le projet est exécuté sous Linux. Le caractère `\` est alors interprété comme
un caractère normal du nom de fichier et `pandas.read_csv()` lève une
`FileNotFoundError`.

Ce problème se produit depuis la racine du projet comme depuis
`src/segmentation`.

Les chemins doivent être construits avec `pathlib.Path`, par exemple :

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "generated"
```

## Problèmes importants

### 1. Mauvais dossier de données

Le script utilise `data/processed/`, alors que le dataset prévu pour le
modeling est `data/generated/`. Il existe actuellement une différence entre
les deux versions :

- `data/generated/sales_data.csv` contient 8 colonnes ;
- `data/processed/sales_data.csv` contient une colonne supplémentaire
  `Revenue`.

Le calcul RFM n'a pas besoin de `Revenue`, car il le recalcule à partir de
`Quantity * Sale_Price`. Il est donc préférable d'utiliser uniformément
`data/generated/`.

### 2. Dossier de sortie dépendant du répertoire courant

```python
OUT = Path("output")
```

Les résultats sont écrits dans le dossier courant et non nécessairement dans
le projet. Il est préférable d'utiliser un chemin basé sur `__file__`, par
exemple :

```python
OUT = PROJECT_ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)
```

### 3. Import dépendant de l'installation du projet

```python
from churn.features import build_feature_set, compute_rfm
```

Cet import fonctionne si le package est installé dans l'environnement
Python. Sinon, le script peut lever `ModuleNotFoundError: churn`. Il faut
exécuter le projet avec son environnement `uv` correctement installé, ou
configurer le package source dans la configuration du projet.

### 4. Traitement des doublons incomplet

Le script détecte les doublons mais ne les supprime pas :

```python
dup_mask = sales.duplicated(
    subset=["Customer_ID", "Product_ID", "Date"],
    keep=False
)
```

Les lignes détectées restent donc utilisées dans le calcul de `Frequency`.
Le message `Lignes conservées` est trompeur. Il faut soit supprimer les
doublons, soit les conserver explicitement et expliquer pourquoi.

## Risques de robustesse dans `features.py`

- `compute_rfm()` vérifie la présence des colonnes, mais pas leurs types,
  leurs valeurs nulles ou leur conversion en dates.
- `Quantity` et `Sale_Price` peuvent produire des valeurs invalides si elles
  contiennent des chaînes ou des valeurs nulles.
- `build_feature_set()` ne vérifie pas l'unicité de `Customer_ID` dans
  `customers_df`. Des doublons clients peuvent multiplier les lignes après la
  fusion.
- Les clients sans achat produisent des valeurs RFM nulles après le `merge`.
  Ces valeurs doivent être traitées avant la normalisation ou le clustering.
- `compute_rfm` est importée dans `client_segmentation.py` mais n'est pas utilisée
  directement.

## Risques de robustesse dans `client_segmentation.py`

- Le script est exécuté entièrement lors de l'import du module. Il serait
  préférable de placer le pipeline dans une fonction `main()` protégée par :

  ```python
  if __name__ == "__main__":
      main()
  ```

- `pd.qcut(..., q=5)` peut échouer sur un autre dataset si les valeurs sont
  trop répétées ou s'il n'existe pas cinq intervalles distincts.
- La boucle K-Means suppose qu'il y a suffisamment de clients et que les
  variables RFM ne sont pas constantes.
- `warnings.filterwarnings("ignore")` masque des avertissements utiles de
  pandas, scikit-learn et seaborn.
- Les tables `products`, `marketing` et `df` sont chargées et fusionnées,
  mais elles ne sont pas utilisées ensuite pour la segmentation. Ces
  opérations ajoutent des dépendances et des risques sans apporter de valeur
  au résultat RFM.
- La date de référence `2025-12-31` est codée en dur. Elle doit rester
  documentée et cohérente avec la période des données.

## Vérifications effectuées sur les données actuelles

Avec les données actuelles :

- 1 000 clients ont au moins une vente ;
- les dates de vente vont jusqu'au `2025-12-31` ;
- les clés `Customer_ID`, `Product_ID` et `Campaign_ID` sont présentes ;
- 6 lignes comportent un doublon selon
  `Customer_ID + Product_ID + Date` ;
- après normalisation temporaire des chemins, le pipeline complet produit
  bien les fichiers de segmentation.

## Corrections prioritaires

1. Renommer et utiliser le dossier `src/segmentation`.
2. Remplacer tous les chemins Windows par des chemins `Path`.
3. Utiliser `data/generated/` comme source du dataset de modeling.
4. Rendre le dossier de sortie indépendant du répertoire courant.
5. Encapsuler l'exécution dans `main()`.
6. Décider explicitement si les doublons doivent être supprimés ou conservés.
7. Ajouter des validations de types, de valeurs nulles et d'identifiants.
8. Rendre le calcul des scores par quantiles robuste aux petits datasets.
