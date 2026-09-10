"""Feature engineering for the churn model (M6).

Builds the customer-level feature set used to train the churn classifier.
Total_Spent from customers_data.csv is intentionally excluded — see
docs/churn.md for the leakage analysis that led to this decision.
"""

from __future__ import annotations

import pandas as pd

REQUIRED_SALES_COLUMNS = {"Customer_ID", "Date", "Quantity", "Sale_Price"}
REQUIRED_CUSTOMER_COLUMNS = {"Customer_ID", "Age", "Gender", "Location", "Churn"}


def compute_rfm(sales_df: pd.DataFrame, reference_date: pd.Timestamp) -> pd.DataFrame:
    """Compute Recency, Frequency, Monetary per customer.

    Recency: days between reference_date and the customer's last purchase.
    Frequency: number of purchases (rows in sales_df).
    Monetary: total revenue (Quantity * Sale_Price), summed per customer.

    reference_date is a required argument, not derived from sales_df, so the
    result stays deterministic and explicit across calls (e.g. re-running
    this on a later export of sales_data.csv won't silently shift the
    reference point).
    """
    missing = REQUIRED_SALES_COLUMNS - set(sales_df.columns)
    if missing:
        raise ValueError(f"sales_df missing required columns: {missing}")

    df = sales_df.copy()
    df["_Revenue"] = df["Quantity"] * df["Sale_Price"]

    rfm = (
        df.groupby("Customer_ID")
        .agg(
            Recency=("Date", lambda x: (reference_date - x.max()).days),
            Frequency=("Date", "count"),
            Monetary=("_Revenue", "sum"),
        )
        .reset_index()
    )

    return rfm


def build_feature_set(
    customers_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    reference_date: pd.Timestamp,
) -> pd.DataFrame:
    """Build the full customer-level feature set for churn modeling.

    Merges RFM features with demographic attributes (Age, Gender, Location)
    and the Churn target. Total_Spent is deliberately not included — it's
    derived from the same _Behavior variable that generates Churn in
    generate_data.py, making it a leakage risk (see docs/churn.md).

    Customers with no purchase history would produce NaN RFM values after
    the merge; there are none in the current dataset (1000/1000 customers
    have at least one sale), but this is not guaranteed for future data, so
    callers should check for NaNs before training rather than assume.
    """
    missing = REQUIRED_CUSTOMER_COLUMNS - set(customers_df.columns)
    if missing:
        raise ValueError(f"customers_df missing required columns: {missing}")

    rfm = compute_rfm(sales_df, reference_date)

    features = customers_df[
        ["Customer_ID", "Age", "Gender", "Location", "Churn"]
    ].merge(rfm, on="Customer_ID", how="left")

    return features


def encode_categorical_features(features_df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode Gender and Location.

    drop_first=True avoids the dummy trap (redundant column that's fully
    determined by the others) — mostly matters for linear models like
    Logistic Regression, harmless but unnecessary to skip for tree-based
    models.
    """
    categorical_columns = ["Gender", "Location"]
    missing = set(categorical_columns) - set(features_df.columns)
    if missing:
        raise ValueError(f"features_df missing columns to encode: {missing}")

    return pd.get_dummies(features_df, columns=categorical_columns, drop_first=True)
