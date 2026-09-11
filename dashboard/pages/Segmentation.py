# =====================================================================
# dashboard/pages/Segmentation.py
# Analyse de la segmentation client
# =====================================================================

import streamlit as st
import plotly.express as px

from utils.data_loader import load_data


# =====================================================================
# TITRE
# =====================================================================

st.title("Segmentation des clients")
st.caption(
    "Analyse des segments clients, de leur valeur et de leur risque de churn"
)


# =====================================================================
# CHARGEMENT DES DONNÉES
# =====================================================================

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


# =====================================================================
# NETTOYAGE DES NOMS DE SEGMENTS
# =====================================================================

# Certains CSV peuvent contenir des espaces avant/après les noms.
segmentation = segmentation.copy()
profil_segment = profil_segment.copy()

segmentation["Segment"] = (
    segmentation["Segment"]
    .astype(str)
    .str.strip()
)

profil_segment["Segment"] = (
    profil_segment["Segment"]
    .astype(str)
    .str.strip()
)


# =====================================================================
# FILTRES - SIDEBAR
# =====================================================================

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


# =====================================================================
# APPLICATION DU FILTRE
# =====================================================================

if selected_segment == "Tous":

    segmentation_filtered = segmentation.copy()
    profil_filtered = profil_segment.copy()

else:

    segmentation_filtered = segmentation[
        segmentation["Segment"] == selected_segment
    ].copy()

    profil_filtered = profil_segment[
        profil_segment["Segment"] == selected_segment
    ].copy()


if segmentation_filtered.empty:

    st.warning(
        "Aucun client disponible pour le segment sélectionné."
    )

    st.stop()


# =====================================================================
# KPI
# =====================================================================

st.subheader("Vue d'ensemble des segments")

col1, col2, col3, col4 = st.columns(4)


# Nombre de clients affichés après filtre
col1.metric(
    "Clients affichés",
    f"{len(segmentation_filtered):,}"
)


# Nombre de segments affichés
col2.metric(
    "Segments",
    f"{segmentation_filtered['Segment'].nunique():,}"
)


# VIP / Champions
vip_count = (
    segmentation_filtered["Segment"]
    .eq("VIP / Champions")
    .sum()
)

col3.metric(
    "Clients VIP / Champions",
    f"{vip_count:,}"
)


# Clients perdus
lost_count = (
    segmentation_filtered["Segment"]
    .eq("Perdus")
    .sum()
)

col4.metric(
    "Clients perdus",
    f"{lost_count:,}"
)


# =====================================================================
# RÉPARTITION DES CLIENTS PAR SEGMENT
# =====================================================================

st.subheader("Répartition des clients par segment")


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


# =====================================================================
# POURCENTAGE DES CLIENTS PAR SEGMENT
# =====================================================================

st.subheader("Répartition en pourcentage")


segment_percentage = (
    segmentation_filtered["Segment"]
    .value_counts(
        normalize=True
    )
    .mul(100)
    .reset_index()
)

segment_percentage.columns = [
    "Segment",
    "Pourcentage"
]


fig_percentage = px.pie(
    segment_percentage,
    names="Segment",
    values="Pourcentage",
    title="Répartition des clients par segment"
)


st.plotly_chart(
    fig_percentage,
    use_container_width=True
)


# =====================================================================
# PROFIL DES SEGMENTS
# =====================================================================

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


profile_columns = [
    col
    for col in profile_columns
    if col in profil_filtered.columns
]


profile = profil_filtered[
    profile_columns
].copy()


# Formatage du churn
if "Taux_churn" in profile.columns:

    profile["Taux_churn"] = (
        profile["Taux_churn"]
        * 100
    ).round(1)


# Les données du CSV sont déjà en pourcentage :
# 13.7 = 13.7 %
# Donc on ne multiplie PAS par 100.
if "Pct_clients" in profile.columns:

    profile["Pct_clients"] = (
        profile["Pct_clients"]
        .round(1)
    )


# Renommage pour affichage
profile = profile.rename(
    columns={
        "Nb_clients": "Nombre de clients",
        "Recency_moy": "Recency moyenne",
        "Freq_moy": "Fréquence moyenne",
        "Monetary_moy": "Valeur monétaire moyenne ($)",
        "Panier_moy": "Panier moyen ($)",
        "Age_moy": "Âge moyen",
        "Taux_churn": "Taux de churn (%)",
        "Pct_clients": "Clients (%)"
    }
)


st.dataframe(
    profile,
    use_container_width=True,
    hide_index=True
)


# =====================================================================
# VALEUR MONÉTAIRE PAR SEGMENT
# =====================================================================

st.subheader("Valeur client par segment")


if (
    "Monetary_moy" in profil_filtered.columns
    and not profil_filtered.empty
):

    monetary_data = (
        profil_filtered
        .sort_values(
            "Monetary_moy",
            ascending=False
        )
        .copy()
    )


    fig_monetary = px.bar(
        monetary_data,
        x="Segment",
        y="Monetary_moy",
        text="Monetary_moy",
        labels={
            "Segment": "Segment",
            "Monetary_moy": "Valeur monétaire moyenne ($)"
        },
        title="Valeur monétaire moyenne par segment"
    )


    fig_monetary.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside"
    )


    st.plotly_chart(
        fig_monetary,
        use_container_width=True
    )

else:

    st.info(
        "Les données Monetary_moy ne sont pas disponibles."
    )


# =====================================================================
# FRÉQUENCE D'ACHAT PAR SEGMENT
# =====================================================================

st.subheader("Fréquence d'achat par segment")


if (
    "Freq_moy" in profil_filtered.columns
    and not profil_filtered.empty
):

    frequency_data = (
        profil_filtered
        .sort_values(
            "Freq_moy",
            ascending=False
        )
        .copy()
    )


    fig_frequency = px.bar(
        frequency_data,
        x="Segment",
        y="Freq_moy",
        text="Freq_moy",
        labels={
            "Segment": "Segment",
            "Freq_moy": "Nombre moyen d'achats"
        },
        title="Fréquence moyenne d'achat par segment"
    )


    fig_frequency.update_traces(
        texttemplate="%{text:.1f}",
        textposition="outside"
    )


    st.plotly_chart(
        fig_frequency,
        use_container_width=True
    )


# =====================================================================
# RECENCY PAR SEGMENT
# =====================================================================

st.subheader("Récence moyenne par segment")


if (
    "Recency_moy" in profil_filtered.columns
    and not profil_filtered.empty
):

    recency_data = (
        profil_filtered
        .sort_values(
            "Recency_moy",
            ascending=True
        )
        .copy()
    )


    fig_recency = px.bar(
        recency_data,
        x="Segment",
        y="Recency_moy",
        text="Recency_moy",
        labels={
            "Segment": "Segment",
            "Recency_moy": "Nombre moyen de jours"
        },
        title="Nombre moyen de jours depuis le dernier achat"
    )


    fig_recency.update_traces(
        texttemplate="%{text:.0f} jours",
        textposition="outside"
    )


    st.plotly_chart(
        fig_recency,
        use_container_width=True
    )


# =====================================================================
# CHURN PAR SEGMENT
# =====================================================================

st.subheader("Churn par segment")


if (
    "Taux_churn" in profil_filtered.columns
    and not profil_filtered.empty
):

    churn_data = profil_filtered.copy()


    fig_churn = px.bar(
        churn_data.sort_values(
            "Taux_churn",
            ascending=False
        ),
        x="Segment",
        y="Taux_churn",
        text="Taux_churn",
        labels={
            "Segment": "Segment",
            "Taux_churn": "Taux de churn"
        },
        title="Taux de churn par segment"
    )


    fig_churn.update_traces(
        texttemplate="%{text:.1%}",
        textposition="outside"
    )


    fig_churn.update_yaxes(
        tickformat=".0%"
    )


    st.plotly_chart(
        fig_churn,
        use_container_width=True
    )

else:

    st.info(
        "Les données de churn par segment ne sont pas disponibles."
    )


# =====================================================================
# COMPARAISON RFM DES SEGMENTS
# =====================================================================

st.subheader("Comparaison des profils RFM")


rfm_columns = [
    "Segment",
    "Recency_moy",
    "Freq_moy",
    "Monetary_moy"
]


if all(
    col in profil_filtered.columns
    for col in rfm_columns
):

    rfm_data = profil_filtered[
        rfm_columns
    ].copy()


    rfm_long = rfm_data.melt(
        id_vars="Segment",
        value_vars=[
            "Recency_moy",
            "Freq_moy",
            "Monetary_moy"
        ],
        var_name="Indicateur",
        value_name="Valeur"
    )


    fig_rfm = px.bar(
        rfm_long,
        x="Segment",
        y="Valeur",
        color="Indicateur",
        barmode="group",
        labels={
            "Segment": "Segment",
            "Valeur": "Valeur moyenne",
            "Indicateur": "Indicateur"
        },
        title="Comparaison des indicateurs RFM"
    )


    st.plotly_chart(
        fig_rfm,
        use_container_width=True
    )


# =====================================================================
# RECOMMANDATIONS MARKETING
# =====================================================================

st.subheader("Recommandations marketing par segment")


if "Recommandation" in segmentation_filtered.columns:

    recommendations = (
        segmentation_filtered[
            [
                "Segment",
                "Recommandation"
            ]
        ]
        .drop_duplicates()
        .sort_values(
            "Segment"
        )
    )


    st.dataframe(
        recommendations,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Aucune recommandation n'est disponible dans le dataset."
    )


# =====================================================================
# RECHERCHE D'UN CLIENT
# =====================================================================

st.subheader("Recherche d'un client")


search_columns = [
    "Customer_ID",
    "Name"
]


search_column = st.selectbox(
    "Rechercher par",
    [
        col
        for col in search_columns
        if col in segmentation.columns
    ]
)


search_value = st.text_input(
    "Valeur recherchée"
)


client_search = segmentation_filtered.copy()


if search_value:

    if search_column == "Customer_ID":

        try:

            customer_id = int(search_value)

            client_search = segmentation_filtered[
                segmentation_filtered["Customer_ID"]
                == customer_id
            ]

        except ValueError:

            st.warning(
                "Veuillez entrer un identifiant client valide."
            )

            client_search = segmentation_filtered.iloc[0:0]

    else:

        client_search = segmentation_filtered[
            segmentation_filtered[
                search_column
            ]
            .astype(str)
            .str.contains(
                search_value,
                case=False,
                na=False
            )
        ]


# =====================================================================
# TABLEAU DES CLIENTS
# =====================================================================

st.subheader("Clients du segment")


columns = [
    "Customer_ID",
    "Name",
    "Age",
    "Gender",
    "Location",
    "Churn",
    "Recency",
    "Frequency",
    "Monetary",
    "Avg_Basket",
    "RFM_score",
    "Cluster",
    "Segment",
    "Recommandation"
]


columns = [
    col
    for col in columns
    if col in client_search.columns
]


st.caption(
    f"{len(client_search):,} client(s) affiché(s)"
)


st.dataframe(
    client_search[
        columns
    ],
    use_container_width=True,
    hide_index=True
)