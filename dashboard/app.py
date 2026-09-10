import streamlit as st

from utils.data_loader import load_data


st.set_page_config(
    page_title="SMD Marketing Dashboard",
    page_icon="📊",
    layout="wide"
)


st.title("Marketing Analytics Dashboard")

st.write(
    "Dashboard du projet Stratégie de Marketing Digital"
)


customers, sales, products, marketing, customer_analytics = load_data()


st.subheader("Données disponibles")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Customers",
    len(customers)
)

col2.metric(
    "Sales",
    len(sales)
)

col3.metric(
    "Products",
    len(products)
)

col4.metric(
    "Campaigns",
    len(marketing)
)

col5.metric(
    "Customer Analytics",
    len(customer_analytics)
)