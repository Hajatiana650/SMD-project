"""Score all customers with the persisted segmentation model.

Run with: uv run python src/segmentation/predict_segmentation.py

Reuses the scaler, K-Means model, log-transform columns, and quantile
bin edges saved by train_segmentation.py — transform/predict only, no
re-fitting, so segment assignments stay consistent across runs (see
docs/segmentation.md for the problem this fixes).
"""

from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from churn.features import build_feature_set
from segmentation.rfm import (
    RFM_COLUMNS,
    add_avg_basket,
    build_segment_profile,
    label_from_rfm,
    log_transform_skewed,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "generated"
MODELS_DIR = PROJECT_ROOT / "models" / "segmentation"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "segmentation"
REFERENCE_DATE = pd.Timestamp("2025-12-31")

RECOMMENDATIONS = {
    "VIP / Champions": "Programme VIP, offres exclusives, service premium, early access.",
    "Clients fidèles": "Cross-sell / upsell, programme de parrainage, abonnement.",
    "Gros panier occasionnel": "Relance ciblée sur produits premium, offres personnalisées.",
    "À risque": "Campagne de réactivation urgente, remise personnalisée.",
    "Nouveaux / à activer": "Onboarding, offre de bienvenue, incitation 2ème achat.",
    "Perdus": "Email win-back, enquête satisfaction, dernière chance.",
    "Occasionnels": "Nurturing, contenus, promotions saisonnières.",
}


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    customers = pd.read_csv(DATA_DIR / "customers_data.csv", parse_dates=["Join_Date"])
    sales = pd.read_csv(DATA_DIR / "sales_data.csv", parse_dates=["Date"])
    return customers, sales


def apply_quantile_edges(rfm: pd.DataFrame, edges: dict) -> pd.DataFrame:
    """Score R/F/M using bin edges learned at train time (cut, not qcut).

    Recency is inverted: a smaller Recency (recent purchase) earns a
    higher score, hence labels=[5, 4, 3, 2, 1] instead of [1..5].
    """
    scored = rfm.copy()
    scored["R_score"] = pd.cut(
        scored["Recency"],
        bins=edges["Recency"],
        labels=[5, 4, 3, 2, 1],
        include_lowest=True,
    ).astype(int)
    scored["F_score"] = pd.cut(
        scored["Frequency"],
        bins=edges["Frequency"],
        labels=[1, 2, 3, 4, 5],
        include_lowest=True,
    ).astype(int)
    scored["M_score"] = pd.cut(
        scored["Monetary"],
        bins=edges["Monetary"],
        labels=[1, 2, 3, 4, 5],
        include_lowest=True,
    ).astype(int)
    scored["RFM_score"] = scored["R_score"] + scored["F_score"] + scored["M_score"]
    return scored


def save_visualizations(rfm: pd.DataFrame) -> None:
    churn_table = (
        pd.crosstab(rfm["Segment"], rfm["Churn"], normalize="index") * 100
    ).round(2)
    churn_table.columns = [f"Churn={c} (%)" for c in churn_table.columns]
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
        lo, hi = rfm_norm[column].min(), rfm_norm[column].max()
        rfm_norm[column] = 0.0 if hi == lo else (rfm_norm[column] - lo) / (hi - lo)
    heat = rfm_norm.groupby("Segment")[RFM_COLUMNS].mean().round(2)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(heat, annot=True, cmap="YlGnBu", ax=ax)
    ax.set_title("Profil RFM normalisé par segment")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "heatmap_rfm.png", dpi=120)
    plt.close(fig)


def main() -> None:
    customers, sales = load_data()
    features = build_feature_set(customers, sales, REFERENCE_DATE)

    rfm = features.merge(
        customers[["Customer_ID", "Name", "Join_Date"]],
        on="Customer_ID",
        how="left",
        validate="one_to_one",
    )
    rfm = add_avg_basket(rfm)

    scaler = joblib.load(MODELS_DIR / "scaler.joblib")
    kmeans = joblib.load(MODELS_DIR / "kmeans_model.joblib")
    log_columns = joblib.load(MODELS_DIR / "log_columns.joblib")
    quantile_edges = joblib.load(MODELS_DIR / "quantile_edges.joblib")

    rfm_log = log_transform_skewed(rfm, log_columns)
    scaled = scaler.transform(rfm_log[RFM_COLUMNS])  # transform only, no fit

    rfm["Cluster"] = kmeans.predict(scaled)  # predict only, no fit
    rfm = apply_quantile_edges(rfm, quantile_edges)
    rfm["Segment"] = rfm.apply(label_from_rfm, axis=1)
    rfm["Recommandation"] = rfm["Segment"].map(RECOMMENDATIONS)

    profile = build_segment_profile(rfm)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_visualizations(rfm)

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
        OUTPUT_DIR / "segmentation_clients.csv", index=False, encoding="utf-8-sig"
    )
    profile.to_csv(OUTPUT_DIR / "profil_segments.csv", encoding="utf-8-sig")

    print(f"Nombre de clients : {len(rfm)}")
    print(rfm["Segment"].value_counts())
    print(f"Résultats sauvegardés dans {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
