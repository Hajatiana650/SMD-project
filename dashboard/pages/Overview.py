import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data


st.title("Vue globale")
st.caption("Synthèse des performances commerciales")


# ---------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------
customers, sales, products, marketing, customer_analytics, segmentation, profil_segment = load_data()

# ---------------------------------------------------------------------
# Préparation
# ---------------------------------------------------------------------
df = sales.merge(
    products,
    on="Product_ID",
    how="left"
)

df["Date"] = pd.to_datetime(df["Date"])

# Sale_Price représente le montant total de la ligne de vente
df["Revenue"] = df["Sale_Price"]


# ---------------------------------------------------------------------
# Filtres
# ---------------------------------------------------------------------
st.sidebar.header("Filtres")

channels = sorted(
    df["Channel"].dropna().unique().tolist()
)

selected_channels = st.sidebar.multiselect(
    "Canal",
    channels,
    default=channels
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Période",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# ---------------------------------------------------------------------
# Application des filtres
# ---------------------------------------------------------------------
df_filtered = df[
    df["Channel"].isin(selected_channels)
].copy()

if len(selected_dates) == 2:

    start_date, end_date = selected_dates

    df_filtered = df_filtered[
        (df_filtered["Date"].dt.date >= start_date)
        & (df_filtered["Date"].dt.date <= end_date)
    ]


if df_filtered.empty:
    st.warning("Aucune donnée disponible avec ces filtres.")
    st.stop()


# ---------------------------------------------------------------------
# KPI
# ---------------------------------------------------------------------
st.subheader("Indicateurs clés")

col1, col2, col3, col4, col5 = st.columns(5)

total_revenue = df_filtered["Revenue"].sum()
total_sales = len(df_filtered)
average_basket = df_filtered["Revenue"].mean()
total_quantity = df_filtered["Quantity"].sum()
active_customers = df_filtered["Customer_ID"].nunique()

col1.metric("CA total", f"{total_revenue:,.0f} $")
col2.metric("Ventes", f"{total_sales:,}")
col3.metric("Panier moyen", f"{average_basket:,.2f} $")
col4.metric("Quantité vendue", f"{total_quantity:,}")
col5.metric("Clients actifs", f"{active_customers:,}")


# ---------------------------------------------------------------------
# Churn global
# ---------------------------------------------------------------------
if "Churn" in customers.columns:

    st.subheader("Churn")

    churn_rate = customers["Churn"].mean() * 100
    churned = int(customers["Churn"].sum())

    col1, col2 = st.columns(2)

    col1.metric(
        "Taux de churn",
        f"{churn_rate:.1f} %"
    )

    col2.metric(
        "Clients churnés",
        f"{churned:,} / {len(customers):,}"
    )


# ---------------------------------------------------------------------
# Evolution du CA
# ---------------------------------------------------------------------
st.subheader("Évolution du chiffre d'affaires")

df_time = df_filtered.copy()

df_time["Mois"] = (
    df_time["Date"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

ca_monthly = (
    df_time
    .groupby("Mois")["Revenue"]
    .sum()
    .reset_index()
)

fig_time = px.line(
    ca_monthly,
    x="Mois",
    y="Revenue",
    markers=True,
    labels={
        "Mois": "Mois",
        "Revenue": "Chiffre d'affaires ($)"
    },
    title="CA mensuel"
)

st.plotly_chart(
    fig_time,
    use_container_width=True
)


# ---------------------------------------------------------------------
# CA par canal
# ---------------------------------------------------------------------
st.subheader("Chiffre d'affaires par canal")

ca_channel = (
    df_filtered
    .groupby("Channel")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_channel = px.bar(
    ca_channel,
    x="Channel",
    y="Revenue",
    text="Revenue",
    labels={
        "Channel": "Canal",
        "Revenue": "Chiffre d'affaires ($)"
    }
)

st.plotly_chart(
    fig_channel,
    use_container_width=True
)


# ---------------------------------------------------------------------
# CA par catégorie
# ---------------------------------------------------------------------
st.subheader("Chiffre d'affaires par catégorie")

ca_cat = (
    df_filtered
    .groupby("Category")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_cat = px.bar(
    ca_cat,
    x="Category",
    y="Revenue",
    text="Revenue",
    labels={
        "Category": "Catégorie",
        "Revenue": "Chiffre d'affaires ($)"
    }
)

st.plotly_chart(
    fig_cat,
    use_container_width=True
)


# ---------------------------------------------------------------------
# CA par marque
# ---------------------------------------------------------------------
st.subheader("Chiffre d'affaires par marque")

ca_brand = (
    df_filtered
    .groupby("Brand")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_brand = px.bar(
    ca_brand,
    x="Brand",
    y="Revenue",
    text="Revenue",
    labels={
        "Brand": "Marque",
        "Revenue": "Chiffre d'affaires ($)"
    }
)

st.plotly_chart(
    fig_brand,
    use_container_width=True
)