import streamlit as st
from utils.data_loader import load_data


# Configuration
st.set_page_config(
    page_title="SMD Marketing Dashboard",
    page_icon="📊",
    layout="wide"
)


# Chargement des données
customers, sales, products, marketing, customer_analytics = load_data()


# Titre
st.title("Marketing Analytics Dashboard")
st.write("Analyse et optimisation marketing basée sur la segmentation client")


# KPIs
st.subheader("Vue générale")

total_customers = len(customers)
total_sales = len(sales)
total_products = len(products)
total_campaigns = len(marketing)

# Sale_Price représente le montant total de chaque ligne de vente
total_revenue = sales["Sale_Price"].sum()


col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Clients", total_customers)
col2.metric("Ventes", total_sales)
col3.metric("Produits", total_products)
col4.metric("Campagnes", total_campaigns)
col5.metric("Chiffre d'affaires", f"{total_revenue:,.2f}")


# Informations
st.divider()

st.subheader("État des données")

col1, col2 = st.columns(2)

with col1:
    st.write("**Tables disponibles**")
    st.write("• Customers")
    st.write("• Sales")
    st.write("• Products")
    st.write("• Marketing")

with col2:
    st.write("**Dataset client**")
    st.write(f"{len(customer_analytics)} clients analysés")