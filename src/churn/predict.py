"""Score all customers with the trained churn model (M6).

Run with: uv run python src/churn/predict.py

Loads the persisted model/scaler/feature_columns from train.py and applies
them to the full customer base (not just the test split), producing the
churn_probability output consumed by Binôme 1 (dashboard) and Binôme 3
(marketing strategy).
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from churn.features import build_feature_set, encode_categorical_features

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "generated"
MODELS_DIR = PROJECT_ROOT / "models" / "churn"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "churn"
REFERENCE_DATE = pd.Timestamp("2025-12-31")


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    customers = pd.read_csv(DATA_DIR / "customers_data.csv")
    sales = pd.read_csv(DATA_DIR / "sales_data.csv", parse_dates=["Date"])
    return customers, sales


def main() -> None:
    customers, sales = load_data()

    features = build_feature_set(customers, sales, REFERENCE_DATE)
    features_encoded = encode_categorical_features(features)

    model = joblib.load(MODELS_DIR / "churn_model.joblib")
    scaler = joblib.load(MODELS_DIR / "scaler.joblib")
    feature_columns = joblib.load(MODELS_DIR / "feature_columns.joblib")

    X = features_encoded.drop(columns=["Customer_ID", "Churn"])
    X = X.reindex(columns=feature_columns, fill_value=0)

    X_scaled = scaler.transform(X)
    churn_probability = model.predict_proba(X_scaled)[:, 1]

    predictions = pd.DataFrame(
        {
            "Customer_ID": features_encoded["Customer_ID"],
            "churn_probability": churn_probability.round(4),
        }
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(OUTPUT_DIR / "predictions.csv", index=False)

    print(predictions.describe())
    print(f"Predictions saved to {OUTPUT_DIR / 'predictions.csv'}")


if __name__ == "__main__":
    main()
