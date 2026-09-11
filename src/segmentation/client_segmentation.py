"""Customer segmentation with RFM features and K-Means clustering."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

from churn.features import build_feature_set

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "generated"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "segmentation"
REFERENCE_DATE = pd.Timestamp("2025-12-31")
RANDOM_STATE = 42
RFM_COLUMNS = ["Recency", "Frequency", "Monetary"]


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and validate the customer and sales datasets."""
    customer_path = DATA_DIR / "customers_data.csv"
    sales_path = DATA_DIR / "sales_data.csv"

    customers = pd.read_csv(customer_path, parse_dates=["Join_Date"])
    sales = pd.read_csv(sales_path, parse_dates=["Date"])

    required_customers = {
        "Customer_ID",
        "Name",
        "Age",
        "Gender",
        "Location",
        "Join_Date",
        "Churn",
    }
    required_sales = {
        "Sale_ID",
        "Customer_ID",
        "Date",
        "Quantity",
        "Sale_Price",
    }

    missing_customers = required_customers - set(customers.columns)
    missing_sales = required_sales - set(sales.columns)
    if missing_customers or missing_sales:
        raise ValueError(
            "Colonnes manquantes - "
            f"customers_data.csv: {sorted(missing_customers)}; "
            f"sales_data.csv: {sorted(missing_sales)}"
        )

    if customers["Customer_ID"].duplicated().any():
        raise ValueError("Customer_ID doit être unique dans customers_data.csv")

    for column in ["Quantity", "Sale_Price"]:
        sales[column] = pd.to_numeric(sales[column], errors="raise")

    if sales[["Customer_ID", "Date", "Quantity", "Sale_Price"]].isna().any().any():
        raise ValueError("sales_data.csv contient des valeurs nulles obligatoires")

    unknown_customers = set(sales["Customer_ID"]) - set(customers["Customer_ID"])
    if unknown_customers:
        raise ValueError(
            f"Ventes associées à des clients inconnus: {sorted(unknown_customers)[:5]}"
        )

    duplicate_columns = ["Customer_ID", "Product_ID", "Date"]
    if set(duplicate_columns).issubset(sales.columns):
        duplicate_mask = sales.duplicated(subset=duplicate_columns, keep="first")
        duplicate_count = int(duplicate_mask.sum())
        if duplicate_count:
            print(f"\nDoublons supprimés : {duplicate_count} lignes")
            sales = sales.loc[~duplicate_mask].copy()

    return customers, sales


def add_quantile_scores(rfm: pd.DataFrame) -> pd.DataFrame:
    """Add stable five-level RFM scores, including for tied values."""
    scored = rfm.copy()
    quantile_count = min(5, len(scored))
    if quantile_count < 2:
        raise ValueError("Au moins deux clients sont nécessaires pour les scores RFM")

    scored["R_score"] = pd.qcut(
        scored["Recency"].rank(method="first"),
        q=quantile_count,
        labels=list(range(quantile_count, 0, -1)),
    ).astype(int)
    scored["F_score"] = pd.qcut(
        scored["Frequency"].rank(method="first"),
        q=quantile_count,
        labels=list(range(1, quantile_count + 1)),
    ).astype(int)
    scored["M_score"] = pd.qcut(
        scored["Monetary"].rank(method="first"),
        q=quantile_count,
        labels=list(range(1, quantile_count + 1)),
    ).astype(int)
    scored["RFM_score"] = (
        scored["R_score"] + scored["F_score"] + scored["M_score"]
    )
    return scored


def label_from_rfm(row: pd.Series) -> str:
    """Assign a marketing segment from RFM scores."""
    recency = row["R_score"]
    frequency = row["F_score"]
    monetary = row["M_score"]

    if recency >= 4 and frequency >= 4 and monetary >= 4:
        return "VIP / Champions"
    if recency >= 3 and frequency >= 4 and monetary >= 3:
        return "Clients fidèles"
    if monetary >= 4 and frequency <= 2:
        return "Gros panier occasionnel"
    if recency <= 2 and frequency >= 3 and monetary >= 3:
        return "À risque"
    if recency >= 4 and frequency <= 2 and monetary <= 2:
        return "Nouveaux / à activer"
    if recency <= 2 and frequency <= 2 and monetary <= 2:
        return "Perdus"
    return "Occasionnels"


def choose_cluster_count(features: np.ndarray) -> tuple[int, dict[str, list[float]]]:
    """Select K using silhouette, Calinski-Harabasz and Davies-Bouldin scores."""
    sample_count = len(features)
    if sample_count < 3:
        raise ValueError("Au moins trois clients sont nécessaires pour K-Means")

    k_range = range(2, min(10, sample_count - 1) + 1)
    inertias: list[float] = []
    silhouettes: list[float] = []
    ch_scores: list[float] = []
    db_scores: list[float] = []

    for k in k_range:
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        labels = model.fit_predict(features)
        inertias.append(model.inertia_)
        silhouettes.append(silhouette_score(features, labels))
        ch_scores.append(calinski_harabasz_score(features, labels))
        db_scores.append(davies_bouldin_score(features, labels))

    k_values = list(k_range)
    votes = [
        k_values[int(np.argmax(silhouettes))],
        k_values[int(np.argmax(ch_scores))],
        k_values[int(np.argmin(db_scores))],
    ]
    counts = pd.Series(votes).value_counts()
    best_k = max(3, int(counts.index[0])) if len(k_values) >= 3 else int(counts.index[0])
    best_k = min(best_k, k_values[-1])

    scores = {
        "k": k_values,
        "inertias": inertias,
        "silhouettes": silhouettes,
        "ch_scores": ch_scores,
        "db_scores": db_scores,
    }
    return best_k, scores


def save_cluster_diagnostics(scores: dict[str, list[float]]) -> None:
    """Save the metrics used to select the number of clusters."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    charts = [
        ("inertias", "Elbow (inertie)"),
        ("silhouettes", "Silhouette"),
        ("ch_scores", "Calinski-Harabasz"),
        ("db_scores", "Davies-Bouldin"),
    ]
    for axis, (key, title) in zip(axes.flat, charts):
        axis.plot(scores["k"], scores[key], marker="o")
        axis.set_title(title)
        axis.set_xlabel("k")
        axis.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "choix_k.png", dpi=120)
    plt.close(fig)


def build_segment_profile(rfm: pd.DataFrame) -> pd.DataFrame:
    """Build the aggregate profile exported for each segment."""
    profile = (
        rfm.groupby("Segment")
        .agg(
            Nb_clients=("Customer_ID", "count"),
            Recency_moy=("Recency", "mean"),
            Freq_moy=("Frequency", "mean"),
            Monetary_moy=("Monetary", "mean"),
            Panier_moy=("Avg_Basket", "mean"),
            Age_moy=("Age", "mean"),
            Taux_churn=("Churn", "mean"),
        )
        .round(2)
    )
    profile["Pct_clients"] = (
        profile["Nb_clients"] / len(rfm) * 100
    ).round(1)
    return profile


def save_outputs(rfm: pd.DataFrame, profile: pd.DataFrame) -> None:
    """Save segmentation tables and visualizations."""
    recommendations = {
        "VIP / Champions": "Programme VIP, offres exclusives, service premium, early access.",
        "Clients fidèles": "Cross-sell / upsell, programme de parrainage, abonnement.",
        "Gros panier occasionnel": "Relance ciblée sur produits premium, offres personnalisées.",
        "À risque": "Campagne de réactivation urgente, remise personnalisée.",
        "Nouveaux / à activer": "Onboarding, offre de bienvenue, incitation 2ème achat.",
        "Perdus": "Email win-back, enquête satisfaction, dernière chance.",
        "Occasionnels": "Nurturing, contenus, promotions saisonnières.",
    }
    rfm["Recommandation"] = rfm["Segment"].map(recommendations)

    churn_table = (
        pd.crosstab(rfm["Segment"], rfm["Churn"], normalize="index") * 100
    ).round(2)
    churn_table.columns = [f"Churn={column} (%)" for column in churn_table.columns]
    churn_table = churn_table.sort_values("Churn=1 (%)", ascending=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=churn_table.reset_index(),
        x="Churn=1 (%)",
        y="Segment",
        hue="Segment",
        palette="Reds_r",
        legend=False,
        ax=ax,
    )
    ax.set_title("Taux de churn par segment")
    ax.set_xlabel("Taux de churn (%)")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "churn_par_segment.png", dpi=120)
    plt.close(fig)

    sns.set_style("whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    sns.scatterplot(
        data=rfm,
        x="Recency",
        y="Monetary",
        hue="Segment",
        size="Frequency",
        sizes=(20, 300),
        palette="viridis",
        ax=axes[0],
    )
    axes[0].set_title("Segments (Recency vs Monetary)")
    sns.boxplot(data=rfm, x="Segment", y="Avg_Basket", ax=axes[1])
    axes[1].set_title("Panier moyen par segment")
    axes[1].tick_params(axis="x", rotation=45)
    sns.countplot(
        data=rfm,
        y="Segment",
        order=rfm["Segment"].value_counts().index,
        hue="Segment",
        palette="viridis",
        legend=False,
        ax=axes[2],
    )
    axes[2].set_title("Nombre de clients par segment")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "segments_final.png", dpi=120)
    plt.close(fig)

    rfm_norm = rfm[["Segment", *RFM_COLUMNS]].copy()
    for column in RFM_COLUMNS:
        minimum = rfm_norm[column].min()
        maximum = rfm_norm[column].max()
        if maximum == minimum:
            rfm_norm[column] = 0.0
        else:
            rfm_norm[column] = (rfm_norm[column] - minimum) / (maximum - minimum)
    heat = rfm_norm.groupby("Segment")[RFM_COLUMNS].mean().round(2)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(heat, annot=True, cmap="YlGnBu", ax=ax)
    ax.set_title("Profil RFM normalisé par segment")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "heatmap_rfm.png", dpi=120)
    plt.close(fig)

    export_columns = [
        "Customer_ID",
        "Name",
        "Age",
        "Gender",
        "Location",
        "Churn",
        *RFM_COLUMNS,
        "Avg_Basket",
        "R_score",
        "F_score",
        "M_score",
        "RFM_score",
        "Cluster",
        "Segment",
        "Recommandation",
    ]
    rfm[export_columns].to_csv(
        OUTPUT_DIR / "segmentation_clients.csv",
        index=False,
        encoding="utf-8-sig",
    )
    profile.to_csv(OUTPUT_DIR / "profil_segments.csv", encoding="utf-8-sig")


def main() -> None:
    """Run the complete customer segmentation pipeline."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    customers, sales = load_data()
    features = build_feature_set(customers, sales, REFERENCE_DATE)

    rfm = features.merge(
        customers[["Customer_ID", "Name", "Join_Date"]],
        on="Customer_ID",
        how="left",
        validate="one_to_one",
    )
    if rfm[RFM_COLUMNS].isna().any().any():
        raise ValueError("Les features RFM contiennent des valeurs nulles")
    if (rfm[RFM_COLUMNS] < 0).any().any():
        raise ValueError("Les features RFM contiennent des valeurs négatives")

    rfm["Avg_Basket"] = (rfm["Monetary"] / rfm["Frequency"]).round(2)
    skews = rfm[RFM_COLUMNS].skew()
    columns_to_log = [column for column in RFM_COLUMNS if abs(skews[column]) > 0.75]
    rfm_log = rfm.copy()
    for column in columns_to_log:
        rfm_log[column] = np.log1p(rfm_log[column])

    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(rfm_log[RFM_COLUMNS])
    best_k, scores = choose_cluster_count(scaled_features)
    save_cluster_diagnostics(scores)

    kmeans = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=10)
    rfm["Cluster"] = kmeans.fit_predict(scaled_features)
    rfm = add_quantile_scores(rfm)
    rfm["Segment"] = rfm.apply(label_from_rfm, axis=1)
    profile = build_segment_profile(rfm)

    print(f"\nNombre de clients : {len(rfm)}")
    print("\nRépartition des segments :")
    print(rfm["Segment"].value_counts())
    print("\nTaux de churn par segment :")
    print(pd.crosstab(rfm["Segment"], rfm["Churn"], normalize="index").mul(100).round(2))
    print("\nProfil des segments :\n", profile)

    save_outputs(rfm, profile)
    print(f"\nSEGMENTATION TERMINÉE - résultats dans {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
