import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data


st.title("Analyse marketing")
st.caption("Analyse des campagnes et performances des canaux marketing")


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
customers, sales, products, marketing, customer_analytics, segmentation, profil_segment = load_data()

# ============================================================
# PRÉPARATION DES DONNÉES MARKETING
# ============================================================

marketing_full = marketing.copy()

marketing_full["Start_Date"] = pd.to_datetime(
    marketing_full["Start_Date"]
)

marketing_full["End_Date"] = pd.to_datetime(
    marketing_full["End_Date"]
)

# Éviter les divisions par zéro
marketing_full["CTR"] = (
    marketing_full["Clicks"]
    / marketing_full["Impressions"]
)

marketing_full["Conversion_Rate"] = (
    marketing_full["Conversions"]
    / marketing_full["Clicks"]
)

marketing_full["CPC"] = (
    marketing_full["Budget"]
    / marketing_full["Clicks"]
)

marketing_full["CPA"] = (
    marketing_full["Budget"]
    / marketing_full["Conversions"]
)


# ============================================================
# FILTRE CANAL
# ============================================================

# ============================================================
# FILTRES
# ============================================================

st.sidebar.header("Filtres")

channels = sorted(
    marketing_full["Channel"].dropna().unique().tolist()
)

selected_channels = st.sidebar.multiselect(
    "Canal marketing",
    channels,
    default=channels
)

marketing_filtered = marketing_full[
    marketing_full["Channel"].isin(selected_channels)
].copy()


if marketing_filtered.empty:

    st.warning(
        "Aucune campagne disponible avec les filtres sélectionnés."
    )

    st.stop()


# ============================================================
# KPI
# ============================================================

st.subheader("Indicateurs clés")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Campagnes",
    f"{len(marketing_filtered):,}"
)

col2.metric(
    "Budget total",
    f"{marketing_filtered['Budget'].sum():,.0f} $"
)

col3.metric(
    "Impressions",
    f"{marketing_filtered['Impressions'].sum():,.0f}"
)

col4.metric(
    "Clicks",
    f"{marketing_filtered['Clicks'].sum():,.0f}"
)

col5.metric(
    "Conversions",
    f"{marketing_filtered['Conversions'].sum():,.0f}"
)


# ============================================================
# PERFORMANCES MOYENNES
# ============================================================

st.subheader("Performances marketing")

col1, col2, col3 = st.columns(3)

total_impressions = marketing_filtered["Impressions"].sum()
total_clicks = marketing_filtered["Clicks"].sum()
total_conversions = marketing_filtered["Conversions"].sum()
total_budget = marketing_filtered["Budget"].sum()

ctr_global = (
    total_clicks / total_impressions
    if total_impressions > 0
    else 0
)

conversion_rate_global = (
    total_conversions / total_clicks
    if total_clicks > 0
    else 0
)

cpc_global = (
    total_budget / total_clicks
    if total_clicks > 0
    else 0
)

cpa_global = (
    total_budget / total_conversions
    if total_conversions > 0
    else 0
)

col1.metric(
    "CTR",
    f"{ctr_global * 100:.2f} %"
)

col2.metric(
    "Taux de conversion",
    f"{conversion_rate_global * 100:.2f} %"
)

col3.metric(
    "CPC",
    f"{cpc_global:.2f} $"
)

st.metric(
    "CPA",
    f"{cpa_global:.2f} $"
)


# ============================================================
# BUDGET PAR CANAL
# ============================================================

st.subheader("Budget par canal")

budget_channel = (
    marketing_filtered
    .groupby("Channel")["Budget"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_budget = px.bar(
    budget_channel,
    x="Channel",
    y="Budget",
    text="Budget",
    labels={
        "Channel": "Canal",
        "Budget": "Budget ($)"
    },
    title="Budget marketing par canal"
)

st.plotly_chart(
    fig_budget,
    use_container_width=True
)


# ============================================================
# CTR PAR CANAL
# ============================================================

st.subheader("CTR par canal")

channel_performance = (
    marketing_filtered
    .groupby("Channel")
    .agg(
        Impressions=("Impressions", "sum"),
        Clicks=("Clicks", "sum"),
        Conversions=("Conversions", "sum"),
        Budget=("Budget", "sum")
    )
    .reset_index()
)

channel_performance["CTR"] = (
    channel_performance["Clicks"]
    / channel_performance["Impressions"]
)

channel_performance["Conversion_Rate"] = (
    channel_performance["Conversions"]
    / channel_performance["Clicks"]
)

channel_performance["CPC"] = (
    channel_performance["Budget"]
    / channel_performance["Clicks"]
)

channel_performance["CPA"] = (
    channel_performance["Budget"]
    / channel_performance["Conversions"]
)

fig_ctr = px.bar(
    channel_performance,
    x="Channel",
    y="CTR",
    text=channel_performance["CTR"].map(
        lambda x: f"{x * 100:.2f}%"
    ),
    labels={
        "Channel": "Canal",
        "CTR": "CTR"
    },
    title="Taux de clic par canal"
)

st.plotly_chart(
    fig_ctr,
    use_container_width=True
)


# ============================================================
# TAUX DE CONVERSION PAR CANAL
# ============================================================

st.subheader("Taux de conversion par canal")

fig_conversion = px.bar(
    channel_performance,
    x="Channel",
    y="Conversion_Rate",
    text=channel_performance["Conversion_Rate"].map(
        lambda x: f"{x * 100:.2f}%"
    ),
    labels={
        "Channel": "Canal",
        "Conversion_Rate": "Taux de conversion"
    },
    title="Conversion des clics par canal"
)

st.plotly_chart(
    fig_conversion,
    use_container_width=True
)


# ============================================================
# CPC / CPA PAR CANAL
# ============================================================

st.subheader("Coûts par canal")

cost_data = channel_performance[
    ["Channel", "CPC", "CPA"]
].copy()

cost_data = cost_data.melt(
    id_vars="Channel",
    value_vars=["CPC", "CPA"],
    var_name="Indicateur",
    value_name="Coût"
)

fig_cost = px.bar(
    cost_data,
    x="Channel",
    y="Coût",
    color="Indicateur",
    barmode="group",
    labels={
        "Channel": "Canal",
        "Coût": "Coût ($)",
        "Indicateur": "Indicateur"
    },
    title="CPC et CPA par canal"
)

st.plotly_chart(
    fig_cost,
    use_container_width=True
)


# ============================================================
# CA DES VENTES PAR CANAL
# ============================================================

st.subheader("Chiffre d'affaires des ventes par canal")

sales_channel = sales.copy()

# Sale_Price = montant total de la ligne
sales_channel["Revenue"] = sales_channel["Sale_Price"]

revenue_channel = (
    sales_channel
    .groupby("Channel")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_revenue = px.bar(
    revenue_channel,
    x="Channel",
    y="Revenue",
    text="Revenue",
    labels={
        "Channel": "Canal",
        "Revenue": "Chiffre d'affaires ($)"
    },
    title="CA des ventes par canal"
)

st.plotly_chart(
    fig_revenue,
    use_container_width=True
)

st.info(
    "Le chiffre d'affaires par canal est présenté à titre "
    "comparatif. Les ventes ne contiennent pas de Campaign_ID, "
    "donc le CA ne peut pas être attribué directement à une campagne."
)


# ============================================================
# TABLEAU DES CAMPAGNES
# ============================================================

st.subheader("Détail des campagnes")

display_columns = [
    "Campaign_ID",
    "Channel",
    "Start_Date",
    "End_Date",
    "Budget",
    "Impressions",
    "Clicks",
    "Conversions",
    "CTR",
    "Conversion_Rate",
    "CPC",
    "CPA"
]

display_columns = [
    col
    for col in display_columns
    if col in marketing_filtered.columns
]

campaign_table = marketing_filtered[
    display_columns
].copy()

campaign_table["CTR"] = (
    campaign_table["CTR"] * 100
).round(2)

campaign_table["Conversion_Rate"] = (
    campaign_table["Conversion_Rate"] * 100
).round(2)

campaign_table["CPC"] = (
    campaign_table["CPC"]
).round(2)

campaign_table["CPA"] = (
    campaign_table["CPA"]
).round(2)

campaign_table = campaign_table.rename(
    columns={
        "CTR": "CTR (%)",
        "Conversion_Rate": "Conversion (%)",
        "CPC": "CPC ($)",
        "CPA": "CPA ($)"
    }
)

st.dataframe(
    campaign_table,
    use_container_width=True,
    hide_index=True
)