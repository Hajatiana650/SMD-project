import streamlit as st
import plotly.express as px
from utils.data_loader import load_data
import pandas as pd

st.title("Vue globale")

customers, sales, products, marketing, customer_analytics = load_data()

df = sales.merge(products, on="Product_ID", how="left")
df["Revenue"] = df["Quantity"] * df["Sale_Price"]


# ---------------------------------------------------------------------
# KPIs (indicateurs clés en haut de page)
# ---------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("CA total", f"{df['Revenue'].sum():,.0f} $")
col2.metric("Nombre de ventes", f"{len(df):,}")
col3.metric("Panier moyen", f"{df['Revenue'].mean():,.2f} $")
col4.metric("Quantité vendue", f"{df['Quantity'].sum():,}")

# ---------------------------------------------------------------------
# TAUX DE CHURN
# ---------------------------------------------------------------------
st.subheader("Taux de churn")

churn_rate = customers["Churn"].mean() * 100

col_a, col_b = st.columns(2)
col_a.metric("Taux de churn", f"{churn_rate:.1f} %")
col_b.metric("Clients churnés", f"{int(customers['Churn'].sum()):,} / {len(customers):,}")


# ---------------------------------------------------------------------
# 6. FILTRE INTERACTIF (par canal)
#    Crée df_filtered qui sera utilisé dans les graphiques ci-dessous
# ---------------------------------------------------------------------
channels = ["Tous"] + sorted(df["Channel"].unique().tolist())
selected_channel = st.selectbox("Filtrer par canal", channels)

if selected_channel == "Tous":
    df_filtered = df
else:
    df_filtered = df[df["Channel"] == selected_channel]

st.caption(f"Affichage : {selected_channel} — {len(df_filtered):,} ventes")

# ---------------------------------------------------------------------
# 6bis. ÉVOLUTION DU CA DANS LE TEMPS
# ---------------------------------------------------------------------
st.subheader("Évolution du chiffre d'affaires")

# On regroupe par mois
df_time = df_filtered.copy()
df_time["Date"] = pd.to_datetime(df_time["Date"])
df_time["Mois"] = df_time["Date"].dt.to_period("M").dt.to_timestamp()

ca_monthly = (
    df_time.groupby("Mois")["Revenue"]
    .sum()
    .reset_index()
)

fig_time = px.line(
    ca_monthly,
    x="Mois",
    y="Revenue",
    markers=True,
    labels={"Mois": "Mois", "Revenue": "Chiffre d'affaires ($)"},
    title="CA mensuel"
)

st.plotly_chart(fig_time, use_container_width=True)

# ---------------------------------------------------------------------
# 6ter. NOMBRE DE VENTES PAR CANAL
# ---------------------------------------------------------------------
st.subheader("Nombre de ventes par canal")

sales_by_channel = (
    df.groupby("Channel")["Sale_ID"]
    .count()
    .sort_values(ascending=False)
    .reset_index()
)
sales_by_channel.columns = ["Channel", "Nb_Ventes"]

fig_sales_channel = px.bar(
    sales_by_channel,
    x="Channel",
    y="Nb_Ventes",
    labels={"Channel": "Canal", "Nb_Ventes": "Nombre de ventes"},
    title="Volume de ventes par canal",
    text="Nb_Ventes"
)

st.plotly_chart(fig_sales_channel, use_container_width=True)

# ---------------------------------------------------------------------
# 7. GRAPHIQUE : Chiffre d'affaires par catégorie
# ---------------------------------------------------------------------
st.subheader("Chiffre d'affaires par catégorie")

ca_cat = (
    df_filtered.groupby("Category")["Revenue"]
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
# 8. GRAPHIQUE : Chiffre d'affaires par marque
# ---------------------------------------------------------------------
st.subheader("Chiffre d'affaires par marque")

ca_brand = (
    df_filtered.groupby("Brand")["Revenue"]
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
# 9. GRAPHIQUE : Chiffre d'affaires par canal (camembert)
#    Note : utilise df (non filtré) pour montrer tous les canaux
# ---------------------------------------------------------------------
st.subheader("Chiffre d'affaires par canal")

ca_channel = (
    df_filtered.groupby("Channel")["Revenue"]
    .sum()
    .sort_values(ascending=False)
)

fig_channel = px.pie(
    ca_channel,
    names=ca_channel.index,
    values=ca_channel.values,
    title="Répartition du CA par canal"
)

st.plotly_chart(fig_channel, use_container_width=True)


# ---------------------------------------------------------------------
# 10. TABLEAU DÉTAILLÉ DES VENTES (filtré)
# ---------------------------------------------------------------------
st.subheader("Données des ventes")

st.dataframe(
    df_filtered,
    use_container_width=True
)