"""Train and persist the final churn model (M6).

Run with: uv run python src/churn/train.py

Trains a Logistic Regression on the RFM + demographic feature set built by
features.py. Logistic Regression was chosen over Random Forest after
comparison in notebooks/model_training.ipynb — equal performance, more
interpretable. See docs/churn.md for the full decision log.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from churn.features import build_feature_set, encode_categorical_features

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "generated"
MODELS_DIR = PROJECT_ROOT / "models" / "churn"
REFERENCE_DATE = pd.Timestamp("2025-12-31")
RANDOM_STATE = 42
TEST_SIZE = 0.2


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    customers = pd.read_csv(DATA_DIR / "customers_data.csv")
    sales = pd.read_csv(DATA_DIR / "sales_data.csv", parse_dates=["Date"])
    return customers, sales


def main() -> None:
    customers, sales = load_data()

    features = build_feature_set(customers, sales, REFERENCE_DATE)
    features_encoded = encode_categorical_features(features)

    X = features_encoded.drop(columns=["Customer_ID", "Churn"])
    y = features_encoded["Churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(random_state=RANDOM_STATE)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]

    print(classification_report(y_test, y_pred))
    print("ROC-AUC:", roc_auc_score(y_test, y_proba))

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODELS_DIR / "churn_model.joblib")
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")
    joblib.dump(list(X.columns), MODELS_DIR / "feature_columns.joblib")

    print(f"Model saved to {MODELS_DIR}")


if __name__ == "__main__":
    main()
