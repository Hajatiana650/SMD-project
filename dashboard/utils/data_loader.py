from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "processed"
SEGMENTATION_DIR = BASE_DIR / "outputs" / "segmentation"
CHURN_DIR = BASE_DIR / "outputs" / "churn"


def load_data():

    customers = pd.read_csv(
        DATA_DIR / "customers_data.csv"
    )

    sales = pd.read_csv(
        DATA_DIR / "sales_data.csv"
    )

    products = pd.read_csv(
        DATA_DIR / "products_data.csv"
    )

    marketing = pd.read_csv(
        DATA_DIR / "marketing_data.csv"
    )

    customer_analytics = pd.read_csv(
        DATA_DIR / "customer_analytics.csv"
    )

    segmentation = pd.read_csv(
        SEGMENTATION_DIR / "segmentation_clients.csv"
    )

    profil_segment = pd.read_csv(
        SEGMENTATION_DIR / "profil_segments.csv"
    )

    churn_predictions = pd.read_csv(
        CHURN_DIR / "predictions.csv"
    )

    return (
        customers,
        sales,
        products,
        marketing,
        customer_analytics,
        segmentation,
        profil_segment,
        churn_predictions
    )