import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data


st.title("Segmentation des clients")
st.caption("Analyse des segments et profils clients")


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
# NETTOYAGE
# ---------------------------------------------------------

segmentation["Segment"] = (
    segmentation["Segment"]
    .astype(str)
    .str.replace("\u00a0", " ", regex=False)
    .str.strip()
)

profil_segment["Segment"] = (
    profil_segment["Segment"]
    .astype(str)
    .str.replace("\u00a0", " ", regex=False)
    .str.strip()
)


# Conversion numérique
for column in [
    "Recency_moy",
    "Freq_moy",
    "Monetary_moy",
    "Panier_moy",
    "Age_moy",
    "Taux_churn",
    "Pct_clients"
]:

    if column in profil_segment.columns:

        profil_segment[column] = pd.to_numeric(
            profil_segment[column],
            errors="coerce"
        )


# ---------------------------------------------------------
# FILTRE
# ---------------------------------------------------------

st.sidebar.header("Filtres")


segments = sorted(
    segmentation["Segment"]
    .dropna()
    .unique()
    .tolist()
)


selected_segment = st.sidebar.selectbox(
    "Segment",
    ["Tous"] + segments
)


if selected_segment == "Tous":

    segmentation_filtered = segmentation.copy()

else:

    segmentation_filtered = segmentation[
        segmentation["Segment"] == selected_segment
    ].copy()


# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------

st.subheader("Vue d'ensemble des segments")


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Clients segmentés",
    f"{len(segmentation_filtered):,}"
)

col2.metric(
    "Segments",
    f"{segmentation['Segment'].nunique():,}"
)


# Ces deux KPI restent globaux
vip_count = (
    segmentation["Segment"]
    .str.strip()
    .eq("VIP / Champions")
    .sum()
)

lost_count = (
    segmentation["Segment"]
    .str.strip()
    .eq("Perdus")
    .sum()
)


col3.metric(
    "Clients VIP / Champions",
    f"{vip_count:,}"
)

col4.metric(
    "Clients perdus",
    f"{lost_count:,}"
)


# ---------------------------------------------------------
# REPARTITION
# ---------------------------------------------------------

st.subheader(
    "Répartition des clients par segment"
)


segment_count = (
    segmentation_filtered
    .groupby("Segment")
    .size()
    .reset_index(name="Nombre_Clients")
    .sort_values(
        "Nombre_Clients",
        ascending=False
    )
)


fig_segments = px.bar(
    segment_count,
    x="Segment",
    y="Nombre_Clients",
    text="Nombre_Clients",
    labels={
        "Segment": "Segment",
        "Nombre_Clients": "Nombre de clients"
    },
    title="Nombre de clients par segment"
)


st.plotly_chart(
    fig_segments,
    use_container_width=True
)


# ---------------------------------------------------------
# PROFIL
# ---------------------------------------------------------

st.subheader("Profil des segments")


profile_columns = [
    "Segment",
    "Nb_clients",
    "Recency_moy",
    "Freq_moy",
    "Monetary_moy",
    "Panier_moy",
    "Age_moy",
    "Taux_churn",
    "Pct_clients"
]


profile = profil_segment[
    [
        col
        for col in profile_columns
        if col in profil_segment.columns
    ]
].copy()


if selected_segment != "Tous":

    profile = profile[
        profile["Segment"] == selected_segment
    ].copy()


if "Taux_churn" in profile.columns:

    profile["Taux_churn"] = (
        profile["Taux_churn"] * 100
    ).round(1)


if "Pct_clients" in profile.columns:

    profile["Pct_clients"] = (
        profile["Pct_clients"]
    ).round(1)


for column in [
    "Recency_moy",
    "Freq_moy",
    "Monetary_moy",
    "Panier_moy",
    "Age_moy"
]:

    if column in profile.columns:

        profile[column] = (
            profile[column]
            .round(2)
        )


profile = profile.rename(
    columns={
        "Nb_clients": "Clients",
        "Recency_moy": "Récence moyenne",
        "Freq_moy": "Fréquence moyenne",
        "Monetary_moy": "Dépense moyenne",
        "Panier_moy": "Panier moyen",
        "Age_moy": "Âge moyen",
        "Taux_churn": "Churn (%)",
        "Pct_clients": "Clients (%)"
    }
)


st.dataframe(
    profile,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# DEPENSE MOYENNE
# ---------------------------------------------------------

st.subheader(
    "Dépense moyenne par segment"
)


monetary_data = profil_segment.copy()


if selected_segment != "Tous":

    monetary_data = monetary_data[
        monetary_data["Segment"] == selected_segment
    ].copy()


if not monetary_data.empty:

    fig_monetary = px.bar(
        monetary_data.sort_values(
            "Monetary_moy",
            ascending=False
        ),
        x="Segment",
        y="Monetary_moy",
        text="Monetary_moy",
        labels={
            "Segment": "Segment",
            "Monetary_moy": "Dépense moyenne ($)"
        },
        title="Dépense moyenne par segment"
    )

    fig_monetary.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    st.plotly_chart(
        fig_monetary,
        use_container_width=True
    )


# ---------------------------------------------------------
# CHURN PAR SEGMENT
# ---------------------------------------------------------

st.subheader("Churn par segment")


churn_data = profil_segment.copy()


if selected_segment != "Tous":

    churn_data = churn_data[
        churn_data["Segment"] == selected_segment
    ].copy()


if not churn_data.empty:

    churn_data["Churn (%)"] = (
        churn_data["Taux_churn"] * 100
    )


    fig_churn = px.bar(
        churn_data.sort_values(
            "Churn (%)",
            ascending=False
        ),
        x="Segment",
        y="Churn (%)",
        text="Churn (%)",
        labels={
            "Segment": "Segment",
            "Churn (%)": "Taux de churn (%)"
        },
        title="Taux de churn par segment"
    )


    fig_churn.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )


    st.plotly_chart(
        fig_churn,
        use_container_width=True
    )


# ---------------------------------------------------------
# RECOMMANDATIONS
# ---------------------------------------------------------

st.subheader("Recommandations par segment")


recommendations = profil_segment[
    ["Segment", "Recommandation"]
].copy()


if selected_segment != "Tous":

    recommendations = recommendations[
        recommendations["Segment"] == selected_segment
    ].copy()


st.dataframe(
    recommendations,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# CLIENTS
# ---------------------------------------------------------

st.subheader("Clients du segment")


client_columns = [
    "Customer_ID",
    "Name",
    "Age",
    "Gender",
    "Location",
    "Recency",
    "Frequency",
    "Monetary",
    "Avg_Basket",
    "RFM_score",
    "Segment",
    "Recommandation"
]


client_columns = [
    col
    for col in client_columns
    if col in segmentation_filtered.columns
]


st.dataframe(
    segmentation_filtered[client_columns],
    use_container_width=True,
    hide_index=True
)