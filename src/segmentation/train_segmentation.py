"""Fit and persist the segmentation model (K-Means + RFM quantile bins).

Run with: uv run python src/segmentation/train_segmentation.py

Persists everything needed to score new customers consistently without
re-fitting: the scaler, the K-Means model, which RFM columns were
log-transformed, and the quantile bin edges used for R/F/M scores.
See docs/segmentation.md for why this split from the original
single-script version.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    calinski_harabasz_score,
    davies_bouldin_score,
    silhouette_score,
)
from sklearn.preprocessing import StandardScaler

from churn.features import build_feature_set
from segmentation.rfm import (
    RFM_COLUMNS,
    SKEW_THRESHOLD,
    add_avg_basket,
    log_transform_skewed,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "generated"
MODELS_DIR = PROJECT_ROOT / "models" / "segmentation"
REFERENCE_DATE = pd.Timestamp("2025-12-31")
RANDOM_STATE = 42
QUANTILE_COUNT = 5


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    customers = pd.read_csv(DATA_DIR / "customers_data.csv", parse_dates=["Join_Date"])
    sales = pd.read_csv(DATA_DIR / "sales_data.csv", parse_dates=["Date"])
    return customers, sales


def choose_cluster_count(features: np.ndarray) -> int:
    """Select K by vote between silhouette, Calinski-Harabasz, Davies-Bouldin.

    Minimum forced to 3: 2 segments doesn't give enough granularity for
    a differentiated marketing strategy (M7) — business decision, not
    purely statistical.
    """
    k_range = range(2, min(10, len(features) - 1) + 1)
    silhouettes, ch_scores, db_scores = [], [], []

    for k in k_range:
        model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        labels = model.fit_predict(features)
        silhouettes.append(silhouette_score(features, labels))
        ch_scores.append(calinski_harabasz_score(features, labels))
        db_scores.append(davies_bouldin_score(features, labels))

    k_values = list(k_range)
    votes = [
        k_values[int(np.argmax(silhouettes))],
        k_values[int(np.argmax(ch_scores))],
        k_values[int(np.argmin(db_scores))],
    ]
    best_k = pd.Series(votes).value_counts().index[0]
    return max(3, int(best_k))


def compute_quantile_edges(rfm: pd.DataFrame) -> dict[str, np.ndarray]:
    """Compute quantile bin edges on the original RFM value scale."""
    edges = {}

    for column in RFM_COLUMNS:
        _, column_edges = pd.qcut(
            rfm[column],
            q=QUANTILE_COUNT,
            retbins=True,
            duplicates="drop",
        )

        if len(column_edges) - 1 < QUANTILE_COUNT:
            print(
                f"⚠️ {column}: seulement "
                f"{len(column_edges) - 1} tranches distinctes possibles "
                f"(attendu {QUANTILE_COUNT})"
            )

        edges[column] = column_edges

    return edges


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

    skews = rfm[RFM_COLUMNS].skew()
    columns_to_log = [c for c in RFM_COLUMNS if abs(skews[c]) > SKEW_THRESHOLD]
    rfm_log = log_transform_skewed(rfm, columns_to_log)

    scaler = StandardScaler()
    scaled = scaler.fit_transform(rfm_log[RFM_COLUMNS])

    best_k = choose_cluster_count(scaled)
    kmeans = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=10)
    kmeans.fit(scaled)

    quantile_edges = compute_quantile_edges(rfm)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")
    joblib.dump(kmeans, MODELS_DIR / "kmeans_model.joblib")
    joblib.dump(columns_to_log, MODELS_DIR / "log_columns.joblib")
    joblib.dump(quantile_edges, MODELS_DIR / "quantile_edges.joblib")

    print(f"K choisi : {best_k}")
    print(f"Colonnes log-transformées : {columns_to_log}")
    print(f"Modèles sauvegardés dans {MODELS_DIR}")


if __name__ == "__main__":
    main()
