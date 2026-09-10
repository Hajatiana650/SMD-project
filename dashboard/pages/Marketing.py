# =====================================================================
# dashboard/pages/Marketing.py
# Analyse des campagnes marketing et de leur performance
# =====================================================================

# ---------------------------------------------------------------------
# 1. IMPORTS
# ---------------------------------------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data


# ---------------------------------------------------------------------
# 2. TITRE
# ---------------------------------------------------------------------
st.title("Analyse marketing")


# ---------------------------------------------------------------------
# 3. CHARGEMENT
# ---------------------------------------------------------------------
customers, sales, products, marketing, customer_analytics = load_data()


# ---------------------------------------------------------------------
# 4. PRÉPARATION
#    - Revenu attribué par campagne (via Campaign_ID dans sales)
#    - Jointure pour calculer le ROI
# ---------------------------------------------------------------------
df = sales.merge(products, on="Product_ID", how="left")
df["Revenue"] = df["Quantity"] * df["Sale_Price"]

# Revenu total généré par chaque campagne
revenue_by_campaign = (
    df.groupby("Campaign_ID")["Revenue"]
    .sum()
    .reset_index()
    .rename(columns={"Revenue": "Revenue_Attribue"})
)

# Fusion avec la table marketing
marketing_full = marketing.merge(
    revenue_by_campaign,
    on="Campaign_ID",
    how="left"
)

# ROI = (Revenu - Coût) / Coût
marketing_full["ROI"] = (
    (marketing_full["Revenue_Attribue"] - marketing_full["Budget"])
    / marketing_full["Budget"]
)

# Taux de conversion = Conversions / Clics
marketing_full["Taux_Conversion"] = (
    marketing_full["Conversions"] / marketing_full["Clicks"]
)


# ---------------------------------------------------------------------
# 5. KPIs
# ---------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Nombre de campagnes", f"{len(marketing):,}")
col2.metric("Budget total", f"{marketing['Budget'].sum():,.0f} $")
col3.metric(
    "Conversions totales",
    f"{marketing['Conversions'].sum():,}"
)
col4.metric(
    "ROI moyen",
    f"{marketing_full['ROI'].mean() * 100:.1f} %"
)


# ---------------------------------------------------------------------
# 6. FILTRE : par canal
# ---------------------------------------------------------------------
channels = ["Tous"] + sorted(marketing["Channel"].unique().tolist())
selected_channel = st.selectbox("Filtrer par canal", channels)

if selected_channel == "Tous":
    df_mkt = marketing_full
else:
    df_mkt = marketing_full[marketing_full["Channel"] == selected_channel]

st.caption(f"Affichage : {selected_channel} — {len(df_mkt):,} campagnes")


# ---------------------------------------------------------------------
# 7. BUDGET PAR CANAL
# ---------------------------------------------------------------------
st.subheader("Budget par canal")

budget_channel = (
    marketing_full.groupby("Channel")["Budget"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_budget = px.bar(
    budget_channel,
    x="Channel",
    y="Budget",
    labels={"Channel": "Canal", "Budget": "Budget total ($)"},
    title="Budget total par canal"
)

st.plotly_chart(fig_budget, use_container_width=True)


# ---------------------------------------------------------------------
# 8. CONVERSIONS PAR CANAL
# ---------------------------------------------------------------------
st.subheader("Conversions par canal")

conv_channel = (
    marketing_full.groupby("Channel")["Conversions"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_conv = px.bar(
    conv_channel,
    x="Channel",
    y="Conversions",
    labels={"Channel": "Canal", "Conversions": "Conversions totales"},
    title="Conversions par canal"
)

st.plotly_chart(fig_conv, use_container_width=True)


# ---------------------------------------------------------------------
# 9. ROI MOYEN PAR CANAL
# ---------------------------------------------------------------------
st.subheader("ROI moyen par canal")

roi_channel = (
    marketing_full.groupby("Channel")["ROI"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

fig_roi = px.bar(
    roi_channel,
    x="Channel",
    y="ROI",
    labels={"Channel": "Canal", "ROI": "ROI moyen (ratio)"},
    title="ROI moyen par canal"
)
fig_roi.update_yaxes(tickformat=".0%")

st.plotly_chart(fig_roi, use_container_width=True)


# ---------------------------------------------------------------------
# 10. SCATTER : BUDGET vs REVENU ATTRIBUÉ
# ---------------------------------------------------------------------
st.subheader("Budget vs Revenu attribué")

fig_scatter = px.scatter(
    df_mkt,
    x="Budget",
    y="Revenue_Attribue",
    color="Channel",
    size="Conversions",
    hover_data=["Campaign_ID"],
    labels={
        "Budget": "Budget ($)",
        "Revenue_Attribue": "Revenu attribué ($)"
    },
    title="Corrélation Budget / Revenu par campagne"
)

st.plotly_chart(fig_scatter, use_container_width=True)


# ---------------------------------------------------------------------
# 11. TABLEAU DES CAMPAGNES (repliable)
# ---------------------------------------------------------------------
with st.expander("Voir le détail des campagnes"):
    cols_to_show = [
        "Campaign_ID", "Channel", "Start_Date", "End_Date",
        "Budget", "Impressions", "Clicks", "Conversions",
        "Revenue_Attribue", "ROI", "Taux_Conversion"
    ]
    st.dataframe(df_mkt[cols_to_show], use_container_width=True)