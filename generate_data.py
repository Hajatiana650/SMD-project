"""
================================================================================
GÉNÉRATEUR DE DONNÉES SYNTHÉTIQUES - PROJET MARKETING & SEGMENTATION CLIENT
================================================================================

OBJECTIF
--------
Générer un jeu de données réaliste et cohérent pour le projet pédagogique
"Analyse & Optimisation Marketing basée sur la Segmentation Client".

FICHIERS GÉNÉRÉS (dans data/generated/)
---------------------------------------
1. customers_data.csv   → Profils clients + Churn + Total_Spent   (1000 lignes)
2. products_data.csv    → Catalogue produits                       (100 lignes)
3. sales_data.csv       → Transactions + Campaign_ID                (~15 000 lignes)
4. marketing_data.csv   → Campagnes marketing                       (~400 lignes)
5. data_dictionary.md   → Dictionnaire des données auto-généré

COUVERTURE DES MODULES
----------------------
M2 (Exploration)   : 4 tables propres, types corrects
M3 (Segmentation)  : Features RFM calculables depuis sales_data
M4 (Profilage)     : Corrélation Âge ↔ Catégorie pour clusters lisibles
M5 (Campagnes)     : Sales.Campaign_ID (100% rempli) → ROI réel par campagne
M6 (Churn/CLV)     : Colonne Churn (0/1) exportée directement
M7 (Stratégie)     : Segments + performances par canal
M8 (Dashboard)     : Toutes les tables joignables par clés

RÈGLES DE COHÉRENCE GARANTIES
-----------------------------
✅ Aucune date d'achat avant la date d'inscription du client
✅ Sale_Price = prix unitaire du produit (Revenue = Quantity × Sale_Price)
✅ Total_Spent = somme exacte des Revenue du client
✅ Impressions ≥ Clics ≥ Conversions pour chaque campagne
✅ End_Date > Start_Date pour chaque campagne
✅ 100% des ventes ont un Campaign_ID dont la campagne est ACTIVE à la date
   de l'achat ET de même canal que la vente
✅ Chaque canal a une couverture continue sur toute la période

AUTEUR   : Équipe Projet SMD IA & PRSD
DATE     : 2026-09
================================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


# =============================================================================
# CONFIGURATION GLOBALE
# =============================================================================
random.seed(42)
np.random.seed(42)
fake = Faker()
Faker.seed(42)

N_CUSTOMERS = 1000
N_PRODUCTS = 100
# Note : N_CAMPAIGNS n'est plus un paramètre fixe. Le nombre de campagnes
# est calculé automatiquement pour garantir une couverture continue.

START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 12, 31)

OUTPUT_DIR = Path("data/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================
def random_date(start, end):
    """Retourne une date aléatoire entre start et end (inclus)."""
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def weighted_choice(items, weights):
    """Tirage aléatoire pondéré."""
    return random.choices(items, weights=weights, k=1)[0]


# =============================================================================
# 1. GÉNÉRATION DES PRODUITS (100 lignes)
# =============================================================================
categories = {
    "Clothing": ["T-shirt", "Shirt", "Jeans", "Hoodie", "Sweater",
                 "Dress", "Skirt", "Shorts", "Pants", "Blouse"],
    "Footwear": ["Sneakers", "Boots", "Sandals", "Running Shoes", "Casual Shoes"],
    "Outerwear": ["Jacket", "Coat", "Blazer", "Raincoat", "Windbreaker"],
    "Accessories": ["Hat", "Cap", "Belt", "Scarf", "Backpack",
                    "Handbag", "Wallet", "Sunglasses"]
}

brands = ["Brand A", "Brand B", "Brand C", "Brand D", "Brand E",
          "Brand F", "Brand G", "Brand H", "Brand I", "Brand J"]

price_ranges = {
    "Accessories": (10, 80),
    "Clothing": (20, 150),
    "Footwear": (50, 220),
    "Outerwear": (80, 300),
}

products_list = []
product_id = 101

for i in range(N_PRODUCTS):
    category = random.choice(list(categories.keys()))
    product_name = random.choice(categories[category])
    low, high = price_ranges[category]
    price = random.uniform(low, high)

    products_list.append({
        "Product_ID": product_id,
        "Product_Name": f"{product_name} {i + 1}",
        "Category": category,
        "Price": round(price, 2),
        "Brand": random.choice(brands)
    })
    product_id += 1

products = pd.DataFrame(products_list)


# =============================================================================
# 2. GÉNÉRATION DES CLIENTS (1000 lignes)
# =============================================================================
locations = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
    "Austin", "Jacksonville"
]

genders = ["Male", "Female"]

customer_behaviors = ["Active", "At Risk", "Churned"]
behavior_weights = [0.60, 0.20, 0.20]

customers_list = []
customer_id = 2001

for _ in range(N_CUSTOMERS):
    join_date = random_date(START_DATE, datetime(2024, 12, 31))
    behavior = weighted_choice(customer_behaviors, behavior_weights)

    customers_list.append({
        "Customer_ID": customer_id,
        "Name": fake.name(),
        "Age": random.randint(18, 70),
        "Gender": random.choice(genders),
        "Location": random.choice(locations),
        "Join_Date": join_date,
        "_Behavior": behavior
    })
    customer_id += 1

customers_internal = pd.DataFrame(customers_list)


# =============================================================================
# 3. GÉNÉRATION DES CAMPAGNES MARKETING — COUVERTURE CONTINUE PAR CANAL
# =============================================================================
# CORRECTION MAJEURE :
# Pour garantir que 100% des ventes puissent être rattachées à une campagne
# active du même canal, on génère une SÉQUENCE CONTINUE de campagnes pour
# chaque canal. Elles se chevauchent légèrement, ce qui garantit qu'à toute
# date il existe AU MOINS une campagne active par canal.
#
# Nombre de campagnes : ~65 par canal × 5 canaux ≈ 325 campagnes au total.
# -----------------------------------------------------------------------------

marketing_channels = ["Online", "In-Store", "Social", "Email", "TV"]

channel_performance = {
    "Online":    {"ctr": (0.02, 0.08), "conversion": (0.04, 0.12)},
    "In-Store":  {"ctr": (0.01, 0.04), "conversion": (0.08, 0.20)},
    "Social":    {"ctr": (0.02, 0.10), "conversion": (0.02, 0.08)},
    "Email":     {"ctr": (0.03, 0.15), "conversion": (0.05, 0.18)},
    "TV":        {"ctr": (0.005, 0.03), "conversion": (0.01, 0.05)},
}

marketing_list = []
campaign_id = 1

for channel in marketing_channels:
    cursor = START_DATE  # On démarre au début de la période

    while cursor < END_DATE:
        # La campagne commence avant le curseur (léger recul aléatoire)
        start_date = cursor - timedelta(days=random.randint(0, 5))
        if start_date < START_DATE:
            start_date = START_DATE

        # Durée entre 20 et 45 jours
        duration = random.randint(20, 45)
        end_date = start_date + timedelta(days=duration)
        if end_date > END_DATE + timedelta(days=15):
            end_date = END_DATE + timedelta(days=15)

        budget = round(random.uniform(500, 10000), 2)
        impressions = random.randint(10000, 500000)

        ctr_min, ctr_max = channel_performance[channel]["ctr"]
        ctr = random.uniform(ctr_min, ctr_max)
        clicks = int(impressions * ctr)

        conv_min, conv_max = channel_performance[channel]["conversion"]
        conversion_rate = random.uniform(conv_min, conv_max)
        conversions = int(clicks * conversion_rate)

        marketing_list.append({
            "Campaign_ID": campaign_id,
            "Channel": channel,
            "Start_Date": start_date,
            "End_Date": end_date,
            "Budget": budget,
            "Impressions": impressions,
            "Clicks": clicks,
            "Conversions": conversions
        })
        campaign_id += 1

        # Le curseur avance à 60-85% de la durée → chevauchement avec la suivante
        cursor = start_date + timedelta(
            days=int(duration * random.uniform(0.60, 0.85))
        )

marketing = pd.DataFrame(marketing_list)


# =============================================================================
# 4. GÉNÉRATION DES VENTES — 100% AVEC Campaign_ID VALIDE
# =============================================================================
# Chaque vente reçoit SYSTÉMATIQUEMENT une campagne dont :
#   - la date d'achat est dans [Start_Date, End_Date]
#   - le canal est identique à celui de la vente
#
# Grâce à la couverture continue, ce matching est TOUJOURS possible.
# -----------------------------------------------------------------------------

sales_list = []
sale_id = 1

products_by_category = {
    cat: products[products["Category"] == cat]
    for cat in categories.keys()
}

active_products = products[products["Price"] <= products["Price"].quantile(0.70)]
premium_products = products[products["Price"] >= products["Price"].quantile(0.60)]


def pick_product_for_customer(customer_age, behavior):
    """Choisit un produit pondéré par l'âge du client et son comportement."""
    if behavior == "Active":
        if random.random() < 0.35:
            return premium_products.sample(1).iloc[0]
        pool = products
    else:
        pool = active_products

    if customer_age < 30:
        preferred = ["Clothing", "Footwear", "Accessories"]
    elif customer_age < 50:
        preferred = list(categories.keys())
    else:
        preferred = ["Outerwear", "Accessories", "Clothing"]

    filtered = pool[pool["Category"].isin(preferred)]
    if filtered.empty:
        filtered = pool
    return filtered.sample(1).iloc[0]


# Pré-indexation des campagnes par canal pour accélérer la recherche
campaigns_by_channel = {
    ch: marketing[marketing["Channel"] == ch].reset_index(drop=True)
    for ch in marketing_channels
}


for _, customer in customers_internal.iterrows():
    behavior = customer["_Behavior"]
    join_date = customer["Join_Date"]
    age = customer["Age"]

    if behavior == "Active":
        last_purchase_limit = END_DATE
        purchase_count = np.random.poisson(random.uniform(12, 25)) + 3
        quantity_max = 5
    elif behavior == "At Risk":
        last_purchase_limit = datetime(2025, 9, 30)
        purchase_count = np.random.poisson(random.uniform(5, 12)) + 1
        quantity_max = 4
    else:  # Churned
        last_purchase_limit = datetime(2025, 4, 30)
        purchase_count = np.random.poisson(random.uniform(2, 7)) + 1
        quantity_max = 3

    if last_purchase_limit < join_date:
        last_purchase_limit = join_date

    for _ in range(purchase_count):
        # --- Date d'achat ---
        if behavior == "Active":
            sale_date = random_date(join_date, last_purchase_limit)
        else:
            total_days = (last_purchase_limit - join_date).days
            if total_days <= 0:
                sale_date = join_date
            else:
                a, b = (2, 4) if behavior == "At Risk" else (2, 6)
                position = np.random.beta(a, b)
                sale_date = join_date + timedelta(days=int(position * total_days))

        # --- Produit + quantité ---
        product = pick_product_for_customer(age, behavior)
        quantity = random.randint(1, quantity_max)

        # --- Canal d'achat (pondéré) ---
        sale_channel = weighted_choice(
            ["Online", "In-Store", "Social", "Email", "TV"],
            [0.55, 0.25, 0.10, 0.05, 0.05]
        )

        # --- Attribution d'une campagne (SYSTÉMATIQUE) ---
        # On cherche les campagnes du bon canal actives à cette date précise.
        channel_campaigns = campaigns_by_channel[sale_channel]
        active_campaigns = channel_campaigns[
            (channel_campaigns["Start_Date"] <= sale_date) &
            (channel_campaigns["End_Date"] >= sale_date)
        ]

        if not active_campaigns.empty:
            campaign_id = int(active_campaigns.sample(1).iloc[0]["Campaign_ID"])
        else:
            # Fallback (ne devrait jamais se produire avec la couverture continue)
            campaign_id = int(channel_campaigns.sample(1).iloc[0]["Campaign_ID"])

        sales_list.append({
            "Sale_ID": sale_id,
            "Product_ID": int(product["Product_ID"]),
            "Customer_ID": int(customer["Customer_ID"]),
            "Date": sale_date,
            "Quantity": quantity,
            "Sale_Price": float(product["Price"]),
            "Channel": sale_channel,
            "Campaign_ID": campaign_id   # <-- TOUJOURS rempli
        })
        sale_id += 1

sales = pd.DataFrame(sales_list)


# =============================================================================
# 5. CALCUL DU TOTAL_SPENT (somme exacte)
# =============================================================================
sales["_Revenue"] = sales["Quantity"] * sales["Sale_Price"]

customer_spending = (
    sales.groupby("Customer_ID")["_Revenue"]
    .sum()
    .reset_index()
    .rename(columns={"_Revenue": "Total_Spent"})
)

sales = sales.drop(columns=["_Revenue"])


# =============================================================================
# 6. FUSION CLIENTS + TOTAL_SPENT + CHURN
# =============================================================================
customers = customers_internal.copy()
customers["Churn"] = customers["_Behavior"].apply(
    lambda b: 0 if b == "Active" else 1
)

customers = customers.merge(
    customer_spending,
    on="Customer_ID",
    how="left"
)

customers["Total_Spent"] = customers["Total_Spent"].fillna(0).round(2)
customers = customers.drop(columns=["_Behavior"])


# =============================================================================
# 7. FORMATAGE DES DATES POUR EXPORT CSV
# =============================================================================
customers["Join_Date"] = pd.to_datetime(customers["Join_Date"]).dt.strftime("%Y-%m-%d")
sales["Date"] = pd.to_datetime(sales["Date"]).dt.strftime("%Y-%m-%d")
marketing["Start_Date"] = pd.to_datetime(marketing["Start_Date"]).dt.strftime("%Y-%m-%d")
marketing["End_Date"] = pd.to_datetime(marketing["End_Date"]).dt.strftime("%Y-%m-%d")


# =============================================================================
# 8. EXPORT DES FICHIERS CSV
# =============================================================================
customers.to_csv(OUTPUT_DIR / "customers_data.csv", index=False)
products.to_csv(OUTPUT_DIR / "products_data.csv", index=False)
sales.to_csv(OUTPUT_DIR / "sales_data.csv", index=False)
marketing.to_csv(OUTPUT_DIR / "marketing_data.csv", index=False)


# =============================================================================
# 9. GÉNÉRATION DU DICTIONNAIRE DE DONNÉES (data_dictionary.md)
# =============================================================================
data_dict_content = """# 📘 Dictionnaire de Données — Data Contract V1

Généré automatiquement par `generate_data.py`.

## 1. `customers_data.csv` (1000 lignes)

| Colonne | Type | Description |
|---------|------|-------------|
| Customer_ID | int | Clé primaire (2001-3000) |
| Name | str | Nom complet du client |
| Age | int | Âge entre 18 et 70 |
| Gender | str | Male / Female |
| Location | str | Ville de résidence (12 villes US) |
| Join_Date | date | Date d'inscription (YYYY-MM-DD) |
| Total_Spent | float | Somme exacte des achats du client |
| Churn | int | 0 = Actif, 1 = À risque/Parti (cible M6) |

## 2. `products_data.csv` (100 lignes)

| Colonne | Type | Description |
|---------|------|-------------|
| Product_ID | int | Clé primaire (101-200) |
| Product_Name | str | Nom du produit |
| Category | str | Clothing / Footwear / Outerwear / Accessories |
| Price | float | Prix unitaire (USD) |
| Brand | str | Marque (Brand A à J) |

## 3. `sales_data.csv` (~15000 lignes)

| Colonne | Type | Description |
|---------|------|-------------|
| Sale_ID | int | Clé primaire de la transaction |
| Product_ID | int | Clé étrangère → products_data |
| Customer_ID | int | Clé étrangère → customers_data |
| Date | date | Date de l'achat (>= Join_Date du client) |
| Quantity | int | Quantité achetée (1 à 5) |
| Sale_Price | float | Prix UNITAIRE au moment de l'achat |
| Channel | str | Online / In-Store / Social / Email / TV |
| Campaign_ID | int | Campagne attribuée (TOUJOURS rempli) |

**⚠️ À retenir** :
- `Revenue = Quantity × Sale_Price` (à calculer par B1/B2)
- **100% des ventes ont un Campaign_ID** valide : la campagne est active à la date de l'achat ET de même canal que la vente.

## 4. `marketing_data.csv` (~325 lignes)

| Colonne | Type | Description |
|---------|------|-------------|
| Campaign_ID | int | Clé primaire |
| Channel | str | Online / In-Store / Social / Email / TV |
| Start_Date | date | Début de la campagne |
| End_Date | date | Fin de la campagne (> Start_Date) |
| Budget | float | Budget dépensé (USD) |
| Impressions | int | Nombre de vues |
| Clicks | int | Nombre de clics (<= Impressions) |
| Conversions | int | Nombre de conversions (<= Clicks) |

**Note** : Les campagnes sont générées avec une couverture continue par canal,
garantissant qu'à toute date il existe au moins une campagne active par canal.

## 5. Relations entre tables (schéma étoile)
"""