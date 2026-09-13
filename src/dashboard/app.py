import streamlit as st


st.set_page_config(
    page_title="SMD Marketing Dashboard",
    page_icon="📊",
    layout="wide"
)


st.title("Marketing Analytics Dashboard")

st.write(
    "Analyse et optimisation marketing basée sur la segmentation client."
)

st.divider()

st.subheader("Modules disponibles")


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Vue globale")
    st.write(
        "Indicateurs clés, évolution du chiffre d'affaires "
        "et performances globales."
    )

with col2:
    st.markdown("### 👥 Clients")
    st.write(
        "Analyse démographique, comportement client et churn."
    )

with col3:
    st.markdown("### 🛍️ Produits")
    st.write(
        "Analyse des produits, catégories et marques."
    )


col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📣 Marketing")
    st.write(
        "Analyse des campagnes et performances des canaux."
    )

with col2:
    st.markdown("### 🤖 Segmentation & Churn")
    st.write(
        "Segmentation client et analyse du risque de churn."
    )


st.info(
    "Utilisez le menu de navigation pour accéder aux différentes analyses."
)