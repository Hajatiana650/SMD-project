"""Shared RFM and labeling logic for the segmentation module.

Pure functions only — no file loading, no model training. Both
train_segmentation.py and predict_segmentation.py import from here so
the logic is written once and reused, not duplicated.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

RFM_COLUMNS = ["Recency", "Frequency", "Monetary"]
SKEW_THRESHOLD = 0.75


def add_avg_basket(rfm: pd.DataFrame) -> pd.DataFrame:
    """Add Avg_Basket = Monetary / Frequency.

    Assumes every customer has Frequency > 0 (true for the current
    dataset). Raises explicitly rather than silently producing inf.
    """
    if (rfm["Frequency"] <= 0).any():
        raise ValueError(
            "Frequency must be > 0 for all customers to compute Avg_Basket"
        )
    result = rfm.copy()
    result["Avg_Basket"] = (result["Monetary"] / result["Frequency"]).round(2)
    return result


def log_transform_skewed(rfm: pd.DataFrame, columns_to_log: list[str]) -> pd.DataFrame:
    """Apply log1p to the given columns.

    columns_to_log must be decided once at train time (based on skew of
    the training population) and reused as-is at predict time.
    """
    result = rfm.copy()
    for column in columns_to_log:
        result[column] = np.log1p(result[column])
    return result


def label_from_rfm(row: pd.Series) -> str:
    """Assign a marketing segment from RFM scores (1-5 scale)."""
    recency, frequency, monetary = row["R_score"], row["F_score"], row["M_score"]

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


def build_segment_profile(rfm: pd.DataFrame) -> pd.DataFrame:
    """Aggregate profile per segment, for reporting."""
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
    profile["Pct_clients"] = (profile["Nb_clients"] / len(rfm) * 100).round(1)
    return profile
