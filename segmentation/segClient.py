
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score
)

from pathlib import Path
import warnings

warnings.filterwarnings("ignore")


# dossier pour les résultats
OUT = Path("output")
OUT.mkdir(exist_ok=True)


# ============================================================
# 1. Chargement des fichiers
# ============================================================

products = pd.read_csv(
    r"..\data\processed\products_data.csv",
    encoding="utf-8-sig"
)

sales = pd.read_csv(
    r"..\data\processed\sales_data.csv",
    parse_dates=["Date"],
    encoding="utf-8-sig"
)

customers = pd.read_csv(
    r"..\data\processed\customers_data.csv",
    parse_dates=["Join_Date"],
    encoding="utf-8-sig"
)

marketing = pd.read_csv(
    r"..\data\processed\marketing_data.csv",
    parse_dates=["Start_Date", "End_Date"],
    encoding="utf-8-sig"
)


print("Colonnes sales :", [repr(c) for c in sales.columns])
print("Colonnes marketing :", [repr(c) for c in marketing.columns])


# ============================================================
# 2. Vérification des doublons
# ============================================================

n_before = len(sales)

dup_mask = sales.duplicated(
    subset=["Customer_ID", "Product_ID", "Date"],
    keep=False
)

print(
    f"\nDoublons détectés : {dup_mask.sum()} lignes"
)

# Si on veut supprimer les doublons :
# sales = sales.drop_duplicates(
#     subset=["Customer_ID", "Product_ID", "Date"],
#     keep="first"
# )

print(f"Lignes conservées : {len(sales)} / {n_before}")


# ============================================================
# 3. Fusion des données
# ============================================================

required_sales_cols = [
    "Product_ID",
    "Customer_ID",
    "Campaign_ID",
    "Sale_ID"
]

missing = [
    c for c in required_sales_cols
    if c not in sales.columns
]

if missing:
    raise KeyError(
        f"Colonnes manquantes dans sales_data.csv : {missing}"
    )


if "Campaign_ID" not in marketing.columns:
    raise KeyError(
        "'Campaign_ID' absent de marketing_data.csv. "
        f"Colonnes disponibles : {list(marketing.columns)}"
    )


# on renomme les colonnes qui peuvent avoir le même nom
marketing_renamed = marketing.rename(columns={
    "Channel": "Campaign_Channel",
    "Budget": "Campaign_Budget",
    "Impressions": "Campaign_Impressions",
    "Clicks": "Campaign_Clicks",
    "Conversions": "Campaign_Conversions",
    "Start_Date": "Campaign_Start",
    "End_Date": "Campaign_End"
})


df = (
    sales
    .merge(
        products,
        on="Product_ID",
        how="left",
        suffixes=("", "_prod")
    )
    .merge(
        customers,
        on="Customer_ID",
        how="left",
        suffixes=("", "_cust")
    )
    .merge(
        marketing_renamed,
        on="Campaign_ID",
        how="left",
        suffixes=("", "_mkt")
    )
)


# montant de chaque vente
df["Revenue"] = df["Quantity"] * df["Sale_Price"]

print(
    f"\nDataset unifié : {df.shape[0]} lignes "
    f"x {df.shape[1]} colonnes"
)


# ============================================================
# 4. Calcul du RFM
# ============================================================

snapshot_date = df["Date"].max() + pd.Timedelta(days=1)


rfm = df.groupby("Customer_ID").agg(
    Recency=(
        "Date",
        lambda x: (snapshot_date - x.max()).days
    ),
    Frequency=("Sale_ID", "nunique"),
    Monetary=("Revenue", "sum")
).reset_index()


# panier moyen
rfm["Avg_Basket"] = (
    rfm["Monetary"] / rfm["Frequency"]
).round(2)


# informations sur les clients
rfm = rfm.merge(
    customers[
        [
            "Customer_ID",
            "Name",
            "Gender",
            "Location",
            "Age",
            "Join_Date",
            "Churn"
        ]
    ],
    on="Customer_ID",
    how="left"
)


print(f"\nNombre de clients : {len(rfm)}")

print(
    rfm[
        [
            "Recency",
            "Frequency",
            "Monetary",
            "Avg_Basket"
        ]
    ].describe().round(2)
)


# ============================================================
# 5. Skew
# ============================================================

print("\nSkew des variables RFM :")

skews = rfm[
    ["Recency", "Frequency", "Monetary"]
].skew()

print(skews.round(3))


SKEW_THRESHOLD = 0.75

cols_to_log = [
    c
    for c in ["Recency", "Frequency", "Monetary"]
    if abs(skews[c]) > SKEW_THRESHOLD
]

print(
    "Colonnes à transformer :",
    cols_to_log if cols_to_log else "aucune"
)


rfm_log = rfm.copy()

for col in cols_to_log:
    rfm_log[col] = np.log1p(rfm_log[col])


# ============================================================
# 6. Normalisation
# ============================================================

scaler = StandardScaler()

X = scaler.fit_transform(
    rfm_log[
        ["Recency", "Frequency", "Monetary"]
    ]
)


# ============================================================
# 7. Recherche du nombre de clusters
# ============================================================

inertias = []
silhouettes = []
ch_scores = []
db_scores = []

K_range = list(range(2, 11))


for k in K_range:

    km = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    labels = km.fit_predict(X)

    inertias.append(km.inertia_)
    silhouettes.append(
        silhouette_score(X, labels)
    )
    ch_scores.append(
        calinski_harabasz_score(X, labels)
    )
    db_scores.append(
        davies_bouldin_score(X, labels)
    )


# graphiques pour comparer les valeurs de k
fig, axes = plt.subplots(
    2,
    2,
    figsize=(14, 9)
)

axes[0, 0].plot(
    K_range,
    inertias,
    marker="o"
)
axes[0, 0].set_title("Elbow (inertie)")


axes[0, 1].plot(
    K_range,
    silhouettes,
    marker="o"
)
axes[0, 1].set_title("Silhouette")


axes[1, 0].plot(
    K_range,
    ch_scores,
    marker="o"
)
axes[1, 0].set_title("Calinski-Harabasz")


axes[1, 1].plot(
    K_range,
    db_scores,
    marker="o"
)
axes[1, 1].set_title("Davies-Bouldin")


for ax in axes.flat:
    ax.set_xlabel("k")
    ax.grid(True, alpha=0.3)


plt.tight_layout()

plt.savefig(
    OUT / "choix_k.png",
    dpi=120
)

plt.close()


# valeurs obtenues avec les trois méthodes
k_sil = K_range[
    int(np.argmax(silhouettes))
]

k_ch = K_range[
    int(np.argmax(ch_scores))
]

k_db = K_range[
    int(np.argmin(db_scores))
]


print(
    f"\nk proposé : "
    f"Silhouette={k_sil}, "
    f"CH={k_ch}, "
    f"DB={k_db}"
)


# vote entre les trois résultats
votes = [
    k_sil,
    k_ch,
    k_db
]

best_k = max(
    3,
    max(set(votes), key=votes.count)
)

print(f"Nombre de clusters choisi : {best_k}")


# ============================================================
# 8. K-Means final
# ============================================================

kmeans = KMeans(
    n_clusters=best_k,
    random_state=42,
    n_init=10
)

rfm["Cluster"] = kmeans.fit_predict(X)


# ============================================================
# 9. Scores RFM
# ============================================================

# Pour Recency, plus petit est meilleur
rfm["R_score"] = pd.qcut(
    rfm["Recency"],
    q=5,
    labels=[5, 4, 3, 2, 1]
).astype(int)


rfm["F_score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5]
).astype(int)


rfm["M_score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5]
).astype(int)


rfm["RFM_score"] = (
    rfm["R_score"]
    + rfm["F_score"]
    + rfm["M_score"]
)


# ============================================================
# 10. Segmentation
# ============================================================

def label_from_rfm(row):

    R = row["R_score"]
    F = row["F_score"]
    M = row["M_score"]

    if R >= 4 and F >= 4 and M >= 4:
        return " VIP / Champions"

    if R >= 3 and F >= 4 and M >= 3:
        return " Clients fidèles"

    if M >= 4 and F <= 2:
        return " Gros panier occasionnel"

    if R <= 2 and F >= 3 and M >= 3:
        return " À risque"

    if R >= 4 and F <= 2 and M <= 2:
        return " Nouveaux / à activer"

    if R <= 2 and F <= 2 and M <= 2:
        return " Perdus"

    return " Occasionnels"


rfm["Segment"] = rfm.apply(
    label_from_rfm,
    axis=1
)


print("\nRépartition des segments :")

print(
    rfm["Segment"].value_counts()
)


# ============================================================
# 11. Vérification avec le churn
# ============================================================

print("\nTaux de churn par segment :")

churn_table = pd.crosstab(
    rfm["Segment"],
    rfm["Churn"],
    normalize="index"
) * 100


churn_table.columns = [
    f"Churn={c} (%)"
    for c in churn_table.columns
]


churn_table = (
    churn_table
    .round(2)
    .sort_values(
        "Churn=1 (%)",
        ascending=False
    )
)

print(churn_table)


fig, ax = plt.subplots(
    figsize=(10, 5)
)

sns.barplot(
    data=churn_table.reset_index(),
    x="Churn=1 (%)",
    y="Segment",
    palette="Reds_r",
    ax=ax
)

ax.set_title(
    "Taux de churn par segment"
)

ax.set_xlabel(
    "Taux de churn (%)"
)

plt.tight_layout()

plt.savefig(
    OUT / "churn_par_segment.png",
    dpi=120
)

plt.close()


# ============================================================
# 12. Profil des segments
# ============================================================

profile = rfm.groupby("Segment").agg(
    Nb_clients=("Customer_ID", "count"),
    Recency_moy=("Recency", "mean"),
    Freq_moy=("Frequency", "mean"),
    Monetary_moy=("Monetary", "mean"),
    Panier_moy=("Avg_Basket", "mean"),
    Age_moy=("Age", "mean"),
    Taux_churn=("Churn", "mean")
).round(2)


profile["Pct_clients"] = (
    profile["Nb_clients"]
    / len(rfm)
    * 100
).round(1)


print(
    "\nProfil des segments :\n",
    profile
)


# ============================================================
# 13. Recommandations
# ============================================================

recommandations = {

    " VIP / Champions":
        "Programme VIP, offres exclusives, service premium, early access.",

    " Clients fidèles":
        "Cross-sell / upsell, programme de parrainage, abonnement.",

    " Gros panier occasionnel":
        "Relance ciblée sur produits premium, offres personnalisées.",

    " À risque":
        "Campagne de réactivation urgente, remise personnalisée.",

    " Nouveaux / à activer":
        "Onboarding, offre de bienvenue, incitation 2ème achat.",

    " Perdus":
        "Email win-back, enquête satisfaction, dernière chance.",

    " Occasionnels":
        "Nurturing, contenus, promotions saisonnières."
}


rfm["Recommandation"] = (
    rfm["Segment"].map(recommandations)
)


# ============================================================
# 14. Graphiques
# ============================================================

sns.set_style("whitegrid")


fig, axes = plt.subplots(
    1,
    3,
    figsize=(18, 5)
)


sns.scatterplot(
    data=rfm,
    x="Recency",
    y="Monetary",
    hue="Segment",
    size="Frequency",
    sizes=(20, 300),
    palette="viridis",
    ax=axes[0]
)

axes[0].set_title(
    "Segments (Recency vs Monetary)"
)


sns.boxplot(
    data=rfm,
    x="Segment",
    y="Avg_Basket",
    ax=axes[1]
)

axes[1].set_title(
    "Panier moyen par segment"
)

axes[1].tick_params(
    axis="x",
    rotation=45
)


sns.countplot(
    data=rfm,
    y="Segment",
    order=rfm[
        "Segment"
    ].value_counts().index,
    palette="viridis",
    ax=axes[2]
)

axes[2].set_title(
    "Nombre de clients par segment"
)


plt.tight_layout()

plt.savefig(
    OUT / "segments_final.png",
    dpi=120
)

plt.close()


# ============================================================
# 15. Heatmap
# ============================================================

rfm_norm = rfm[
    [
        "Segment",
        "Recency",
        "Frequency",
        "Monetary"
    ]
].copy()


for c in [
    "Recency",
    "Frequency",
    "Monetary"
]:

    rfm_norm[c] = (
        rfm_norm[c] - rfm_norm[c].min()
    ) / (
        rfm_norm[c].max()
        - rfm_norm[c].min()
    )


heat = (
    rfm_norm
    .groupby("Segment")
    .mean()
    .round(2)
)


fig, ax = plt.subplots(
    figsize=(8, 5)
)

sns.heatmap(
    heat,
    annot=True,
    cmap="YlGnBu",
    ax=ax
)

ax.set_title(
    "Profil RFM normalisé par segment"
)

plt.tight_layout()

plt.savefig(
    OUT / "heatmap_rfm.png",
    dpi=120
)

plt.close()


# ============================================================
# 16. Export
# ============================================================

cols_export = [
    "Customer_ID",
    "Name",
    "Age",
    "Gender",
    "Location",
    "Churn",
    "Recency",
    "Frequency",
    "Monetary",
    "Avg_Basket",
    "R_score",
    "F_score",
    "M_score",
    "RFM_score",
    "Cluster",
    "Segment",
    "Recommandation"
]


rfm[
    cols_export
].to_csv(
    OUT / "segmentation_clients.csv",
    index=False,
    encoding="utf-8-sig"
)


profile.to_csv(
    OUT / "profil_segments.csv",
    encoding="utf-8-sig"
)
