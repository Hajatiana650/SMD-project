import streamlit as st
import plotly.express as px

from utils.data_loader import load_data


st.title("Analyse des clients")
st.caption("Analyse démographique et comportementale des clients")


(
    customers,
    sales,
    products,
    marketing,
    customer_analytics,
    segmentation,
    profil_segment,
    churn_predictions
) = load_data()


# ---------------------------------------------------------
# FILTRE
# ---------------------------------------------------------

st.sidebar.header("Filtres")

genders = sorted(
    customers["Gender"].dropna().unique().tolist()
)

selected_gender = st.sidebar.selectbox(
    "Genre",
    ["Tous"] + genders
)


if selected_gender == "Tous":

    df_cust = customers.copy()

else:

    df_cust = customers[
        customers["Gender"] == selected_gender
    ].copy()


st.caption(
    f"Clients affichés : {len(df_cust):,}"
)


# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------

st.subheader("Indicateurs clés")

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

    churn_rate = df_cust["Churn"].mean() * 100

    col4.metric(
        "Taux de churn",
        f"{churn_rate:.1f} %"
    )

else:

    col4.metric(
        "Taux de churn",
        "N/A"
    )


# ---------------------------------------------------------
# AGE
# ---------------------------------------------------------

st.subheader("Distribution des âges")

fig_age = px.histogram(
    df_cust,
    x="Age",
    nbins=15,
    labels={
        "Age": "Âge",
        "count": "Nombre de clients"
    }
)

st.plotly_chart(
    fig_age,
    use_container_width=True
)


# ---------------------------------------------------------
# GENRE
# ---------------------------------------------------------

st.subheader("Répartition par genre")

gender_data = (
    df_cust
    .groupby("Gender")
    .size()
    .reset_index(name="Clients")
)


fig_gender = px.pie(
    gender_data,
    names="Gender",
    values="Clients",
    title="Répartition des clients par genre"
)

st.plotly_chart(
    fig_gender,
    use_container_width=True
)


# ---------------------------------------------------------
# LOCALISATION
# ---------------------------------------------------------

st.subheader("Clients par localisation")

location_data = (
    df_cust
    .groupby("Location")
    .size()
    .sort_values(ascending=False)
    .reset_index(name="Clients")
)


fig_location = px.bar(
    location_data,
    x="Location",
    y="Clients",
    text="Clients",
    labels={
        "Location": "Localisation",
        "Clients": "Nombre de clients"
    }
)

st.plotly_chart(
    fig_location,
    use_container_width=True
)


# ---------------------------------------------------------
# CHURN
# ---------------------------------------------------------

if "Churn" in df_cust.columns:

    st.subheader("Répartition du churn")

    churn_data = (
        df_cust
        .groupby("Churn")
        .size()
        .reset_index(name="Clients")
    )

    churn_data["Statut"] = churn_data["Churn"].map(
        {
            0: "Non churn",
            1: "Churn"
        }
    )

    fig_churn = px.pie(
        churn_data,
        names="Statut",
        values="Clients",
        title="Clients churnés / non churnés"
    )

    st.plotly_chart(
        fig_churn,
        use_container_width=True
    )


# ---------------------------------------------------------
# DEPENSE PAR CHURN
# ---------------------------------------------------------

if "Churn" in df_cust.columns:

    st.subheader("Dépense totale selon le churn")

    box_data = df_cust.copy()

    box_data["Statut"] = box_data["Churn"].map(
        {
            0: "Non churn",
            1: "Churn"
        }
    )

    fig_box = px.box(
        box_data,
        x="Statut",
        y="Total_Spent",
        labels={
            "Statut": "Statut",
            "Total_Spent": "Dépense totale ($)"
        }
    )

    st.plotly_chart(
        fig_box,
        use_container_width=True
    )


# ---------------------------------------------------------
# TABLE
# ---------------------------------------------------------

st.subheader("Données clients")

st.dataframe(
    df_cust,
    use_container_width=True,
    hide_index=True
)