import streamlit as st
import plotly.express as px
from utils.data_loader import load_data

st.title("Vue globale")

customers, sales, products, marketing, customer_analytics = load_data()

# Préparation
df = sales.merge(
    products,
    on="Product_ID",
    how="left"
)

st.subheader("Chiffre d'affaires par catégorie")

ca_cat = (
    df.groupby("Category")["Sale_Price"]
    .sum()
    .sort_values(ascending=False)
)

fig_cat = px.bar(
    ca_cat,
    x=ca_cat.index,
    y=ca_cat.values,
    labels={
        "x": "Catégorie",
        "y": "Chiffre d'affaires"
    },
    title="CA par catégorie"
)

st.plotly_chart(fig_cat, use_container_width=True)


st.subheader("Chiffre d'affaires par marque")

ca_brand = (
    df.groupby("Brand")["Sale_Price"]
    .sum()
    .sort_values(ascending=False)
)

fig_brand = px.bar(
    ca_brand,
    x=ca_brand.index,
    y=ca_brand.values,
    labels={
        "x": "Marque",
        "y": "Chiffre d'affaires"
    },
    title="CA par marque"
)

st.plotly_chart(fig_brand, use_container_width=True)


st.subheader("Données des ventes")

st.dataframe(
    df,
    use_container_width=True
)