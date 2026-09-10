# ---------------------------------------------------------------------
# 1. IMPORTS
# ---------------------------------------------------------------------
import streamlit as st
import plotly.express as px
from utils.data_loader import load_data


# ---------------------------------------------------------------------
# 2. TITRE
# ---------------------------------------------------------------------
st.title("Analyse des produits")


# ---------------------------------------------------------------------
# 3. CHARGEMENT
# ---------------------------------------------------------------------
customers, sales, products, marketing, customer_analytics = load_data()


# ---------------------------------------------------------------------
# 4. PRÉPARATION
#    - Jointure ventes + produits
#    - Calcul du vrai Revenue
# ---------------------------------------------------------------------
df = sales.merge(products, on="Product_ID", how="left")
df["Revenue"] = df["Quantity"] * df["Sale_Price"]


# ---------------------------------------------------------------------
# 5. KPIs
# ---------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Nombre de produits", f"{len(products):,}")
col2.metric("Catégories", f"{products['Category'].nunique()}")
col3.metric("Marques", f"{products['Brand'].nunique()}")
col4.metric("Prix moyen", f"{products['Price'].mean():,.2f} $")


# ---------------------------------------------------------------------
# 6. FILTRE : par catégorie
# ---------------------------------------------------------------------
categories = ["Toutes"] + sorted(products["Category"].unique().tolist())
selected_cat = st.selectbox("Filtrer par catégorie", categories)

if selected_cat == "Toutes":
    df_prod = df
else:
    df_prod = df[df["Category"] == selected_cat]

st.caption(f"Affichage : {selected_cat} — {len(df_prod):,} ventes")


# ---------------------------------------------------------------------
# 7. CA PAR CATÉGORIE
# ---------------------------------------------------------------------
st.subheader("Chiffre d'affaires par catégorie")

ca_cat = (
    df.groupby("Category")["Revenue"]
    .sum()
    .sort_values(ascending=False)
)

fig_cat = px.bar(
    ca_cat,
    x=ca_cat.index,
    y=ca_cat.values,
    labels={"x": "Catégorie", "y": "Chiffre d'affaires ($)"},
    title="CA par catégorie"
)

st.plotly_chart(fig_cat, use_container_width=True)


# ---------------------------------------------------------------------
# 8. CA PAR MARQUE
# ---------------------------------------------------------------------
st.subheader("Chiffre d'affaires par marque")

ca_brand = (
    df.groupby("Brand")["Revenue"]
    .sum()
    .sort_values(ascending=False)
)

fig_brand = px.bar(
    ca_brand,
    x=ca_brand.index,
    y=ca_brand.values,
    labels={"x": "Marque", "y": "Chiffre d'affaires ($)"},
    title="CA par marque"
)

st.plotly_chart(fig_brand, use_container_width=True)


# ---------------------------------------------------------------------
# 9. TOP 10 PRODUITS LES PLUS VENDUS (en quantité)
# ---------------------------------------------------------------------
st.subheader("Top 10 produits les plus vendus")

top_products = (
    df_prod.groupby("Product_Name")["Quantity"]
    .sum()
    .nlargest(10)
    .sort_values()
    .reset_index()
)

fig_top = px.bar(
    top_products,
    x="Quantity",
    y="Product_Name",
    orientation="h",
    labels={"Quantity": "Quantité vendue", "Product_Name": ""},
    title="Top 10 produits (par quantité vendue)"
)

st.plotly_chart(fig_top, use_container_width=True)


# ---------------------------------------------------------------------
# 10. PRIX MOYEN PAR CATÉGORIE
# ---------------------------------------------------------------------
st.subheader("Prix moyen par catégorie")

price_by_cat = (
    products.groupby("Category")["Price"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

fig_price = px.bar(
    price_by_cat,
    x="Category",
    y="Price",
    labels={"Category": "Catégorie", "Price": "Prix moyen ($)"},
    title="Prix moyen par catégorie"
)

st.plotly_chart(fig_price, use_container_width=True)


# ---------------------------------------------------------------------
# 11. TABLEAU DÉTAILLÉ (repliable)
# ---------------------------------------------------------------------
with st.expander("Voir le catalogue produits"):
    st.dataframe(products, use_container_width=True)