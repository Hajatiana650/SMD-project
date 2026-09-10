from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"


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

    return (
        customers,
        sales,
        products,
        marketing,
        customer_analytics
    )