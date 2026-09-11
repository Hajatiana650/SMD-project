# =====================================================================
# dashboard/pages/Clients.py
# Analyse démographique des clients + churn
# =====================================================================

# ---------------------------------------------------------------------
# 1. IMPORTS
# ---------------------------------------------------------------------
import streamlit as st
import plotly.express as px
from utils.data_loader import load_data


# ---------------------------------------------------------------------
# 2. TITRE
# ---------------------------------------------------------------------
st.title("Analyse des clients")


# ---------------------------------------------------------------------
# 3. CHARGEMENT
# ---------------------------------------------------------------------
customers, sales, products, marketing, customer_analytics, segmentation, profil_segment = load_data()

# ---------------------------------------------------------------------
# 4. FILTRE
# ---------------------------------------------------------------------

genders = ["Tous"] + sorted(
    customers["Gender"].dropna().unique().tolist()
)

selected_gender = st.selectbox(
    "Filtrer par genre",
    genders
)

if selected_gender == "Tous":
    df_cust = customers.copy()
else:
    df_cust = customers[
        customers["Gender"] == selected_gender
    ].copy()

st.caption(
    f"Affichage : {selected_gender} — "
    f"{len(df_cust):,} clients"
)


# ---------------------------------------------------------------------
# 5. KPI
# ---------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Clients",
    f"{len(df_cust):,}"
)

col2.metric(
    "Âge moyen",
    f"{df_cust['Age'].mean():.1f} ans"
)

col3.metric(
    "Dépense moyenne",
    f"{df_cust['Total_Spent'].mean():,.0f} $"
)

if "Churn" in df_cust.columns:

    col4.metric(
        "Taux de churn",
        f"{df_cust['Churn'].mean() * 100:.1f} %"
    )

else:

    col4.metric(
        "Taux de churn",
        "N/A"
    )

# ---------------------------------------------------------------------
# 6. DISTRIBUTION DE L'ÂGE
# ---------------------------------------------------------------------
st.subheader("Distribution de l'âge")

fig_age = px.histogram(
    df_cust,
    x="Age",
    nbins=20,
    labels={"Age": "Âge", "count": "Nombre de clients"},
    title="Répartition des clients par âge"
)

st.plotly_chart(fig_age, use_container_width=True)


# ---------------------------------------------------------------------
# 7. RÉPARTITION PAR GENRE
# ---------------------------------------------------------------------
st.subheader("Répartition par genre")

gender_count = (
    df_cust.groupby("Gender")["Customer_ID"]
    .count()
    .reset_index()
)
gender_count.columns = ["Gender", "Nb_Clients"]

fig_gender = px.pie(
    gender_count,
    names="Gender",
    values="Nb_Clients",
    title="Répartition Hommes / Femmes"
)

st.plotly_chart(fig_gender, use_container_width=True)


# ---------------------------------------------------------------------
# 8. RÉPARTITION GÉOGRAPHIQUE (par ville)
# ---------------------------------------------------------------------
st.subheader("Répartition géographique")

city_count = (
    df_cust.groupby("Location")["Customer_ID"]
    .count()
    .sort_values(ascending=False)
    .reset_index()
)
city_count.columns = ["Location", "Nb_Clients"]

fig_city = px.bar(
    city_count,
    x="Nb_Clients",
    y="Location",
    orientation="h",
    labels={"Nb_Clients": "Nombre de clients", "Location": ""},
    title="Nombre de clients par ville"
)

st.plotly_chart(fig_city, use_container_width=True)


# ---------------------------------------------------------------------
# 9. CHURN : RÉPARTITION
# ---------------------------------------------------------------------
st.subheader("Répartition du churn")

churn_count = (
    df_cust.groupby("Churn")["Customer_ID"]
    .count()
    .reset_index()
)
churn_count.columns = ["Churn", "Nb_Clients"]
churn_count["Statut"] = churn_count["Churn"].map({0: "Actif", 1: "Churné"})

fig_churn = px.pie(
    churn_count,
    names="Statut",
    values="Nb_Clients",
    title="Clients actifs vs churnés"
)

st.plotly_chart(fig_churn, use_container_width=True)


# ---------------------------------------------------------------------
# 10. TOTAL_SPENT PAR STATUT CHURN (boxplot)
# ---------------------------------------------------------------------
st.subheader("Dépenses selon le statut")

df_cust_plot = df_cust.copy()
df_cust_plot["Statut"] = df_cust_plot["Churn"].map({0: "Actif", 1: "Churné"})

fig_spent = px.box(
    df_cust_plot,
    x="Statut",
    y="Total_Spent",
    color="Statut",
    labels={"Total_Spent": "Total dépensé ($)"},
    title="Distribution des dépenses par statut"
)

st.plotly_chart(fig_spent, use_container_width=True)


# ---------------------------------------------------------------------
# 11. TABLEAU DÉTAILLÉ (optionnel, repliable)
# ---------------------------------------------------------------------
with st.expander("Voir le tableau brut des clients"):
    st.dataframe(df_cust, use_container_width=True)