import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data


st.title("Analyse des produits")
st.caption("Analyse des performances des produits, catégories et marques")


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

customers, sales, products, marketing, customer_analytics, segmentation, profil_segment = load_data()

# ============================================================
# PRÉPARATION DES DONNÉES
# ============================================================

df = sales.merge(
    products,
    on="Product_ID",
    how="left"
)

# Sale_Price = montant total de la ligne de vente
df["Revenue"] = df["Sale_Price"]


# ============================================================
# FILTRE CATÉGORIE
# ============================================================

categories = sorted(
    products["Category"].dropna().unique().tolist()
)

selected_category = st.selectbox(
    "Filtrer par catégorie",
    ["Toutes"] + categories
)

if selected_category == "Toutes":
    df_filtered = df.copy()
    products_filtered = products.copy()
else:
    df_filtered = df[
        df["Category"] == selected_category
    ].copy()

    products_filtered = products[
        products["Category"] == selected_category
    ].copy()


st.caption(
    f"Catégorie sélectionnée : {selected_category}"
)


# ============================================================
# KPI PRODUITS
# ============================================================

st.subheader("Indicateurs clés")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Produits",
    f"{len(products_filtered):,}"
)

col2.metric(
    "Catégories",
    f"{products_filtered['Category'].nunique():,}"
)

col3.metric(
    "Marques",
    f"{products_filtered['Brand'].nunique():,}"
)

col4.metric(
    "Quantité vendue",
    f"{df_filtered['Quantity'].sum():,}"
)


# ============================================================
# TOP 10 PRODUITS PAR QUANTITÉ
# ============================================================

st.subheader("Top 10 produits par quantité vendue")

top_products_quantity = (
    df_filtered
    .groupby("Product_Name")["Quantity"]
    .sum()
    .nlargest(10)
    .sort_values()
    .reset_index()
)

if not top_products_quantity.empty:

    fig_quantity = px.bar(
        top_products_quantity,
        x="Quantity",
        y="Product_Name",
        orientation="h",
        text="Quantity",
        labels={
            "Quantity": "Quantité vendue",
            "Product_Name": ""
        },
        title="Produits les plus vendus"
    )

    st.plotly_chart(
        fig_quantity,
        use_container_width=True
    )

else:
    st.info("Aucune donnée de vente disponible.")


# ============================================================
# TOP 10 PRODUITS PAR CHIFFRE D'AFFAIRES
# ============================================================

st.subheader("Top 10 produits par chiffre d'affaires")

top_products_revenue = (
    df_filtered
    .groupby("Product_Name")["Revenue"]
    .sum()
    .nlargest(10)
    .sort_values()
    .reset_index()
)

if not top_products_revenue.empty:

    fig_revenue = px.bar(
        top_products_revenue,
        x="Revenue",
        y="Product_Name",
        orientation="h",
        text="Revenue",
        labels={
            "Revenue": "Chiffre d'affaires ($)",
            "Product_Name": ""
        },
        title="Produits générant le plus de chiffre d'affaires"
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True
    )

else:
    st.info("Aucune donnée de vente disponible.")


# ============================================================
# PRIX MOYEN PAR CATÉGORIE
# ============================================================

st.subheader("Prix moyen par catégorie")

average_price_category = (
    products_filtered
    .groupby("Category")["Price"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

if not average_price_category.empty:

    fig_price = px.bar(
        average_price_category,
        x="Category",
        y="Price",
        text="Price",
        labels={
            "Category": "Catégorie",
            "Price": "Prix moyen ($)"
        },
        title="Prix moyen des produits par catégorie"
    )

    st.plotly_chart(
        fig_price,
        use_container_width=True
    )


# ============================================================
# RÉPARTITION DES PRODUITS PAR CATÉGORIE
# ============================================================

st.subheader("Répartition des produits par catégorie")

category_count = (
    products_filtered
    .groupby("Category")
    .size()
    .reset_index(name="Nombre_Produits")
)

if not category_count.empty:

    fig_category = px.pie(
        category_count,
        names="Category",
        values="Nombre_Produits",
        title="Nombre de produits par catégorie"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


# ============================================================
# CATALOGUE DES PRODUITS
# ============================================================

st.subheader("Catalogue des produits")

catalogue_columns = [
    "Product_ID",
    "Product_Name",
    "Category",
    "Price",
    "Brand"
]

catalogue_columns = [
    col for col in catalogue_columns
    if col in products_filtered.columns
]

catalogue = products_filtered[catalogue_columns].copy()

st.dataframe(
    catalogue,
    use_container_width=True,
    hide_index=True
)