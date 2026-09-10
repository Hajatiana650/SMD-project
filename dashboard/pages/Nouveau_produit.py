import streamlit as st
import plotly.express as px

st.title("Opportunités de nouveaux produits")

# df doit contenir :
# Customer_ID, Category, Revenue, Brand
# rfm doit contenir :
# Customer_ID, Segment


# CA par segment et catégorie
seg_cat = (
    df.merge(
        rfm[["Customer_ID", "Segment"]],
        on="Customer_ID"
    )
    .groupby(["Segment", "Category"])["Revenue"]
    .sum()
    .reset_index()
)

# Nombre de clients d'un segment qui achètent une catégorie
seg_cat_clients = (
    df.merge(
        rfm[["Customer_ID", "Segment"]],
        on="Customer_ID"
    )
    .groupby(["Segment", "Category"])["Customer_ID"]
    .nunique()
    .reset_index(name="NbClients")
)

# Taille de chaque segment
seg_size = (
    rfm.groupby("Segment")["Customer_ID"]
    .count()
    .reset_index(name="SegmentSize")
)

# Calcul des opportunités
opp = (
    seg_cat
    .merge(seg_cat_clients, on=["Segment", "Category"])
    .merge(seg_size, on="Segment")
)

opp["Part"] = (
    opp.groupby("Segment")["Revenue"]
    .transform(lambda x: x / x.sum())
)

opp["Penetration"] = (
    opp["NbClients"] / opp["SegmentSize"]
)

opp["Opportunity"] = (
    opp["Part"] * (1 - opp["Penetration"])
)

# Top opportunités
top_opportunities = (
    opp.sort_values("Opportunity", ascending=False)
    .head(10)
)

st.subheader("Top 10 opportunités")

st.dataframe(
    top_opportunities[
        [
            "Segment",
            "Category",
            "Revenue",
            "NbClients",
            "SegmentSize",
            "Penetration",
            "Opportunity"
        ]
    ],
    use_container_width=True
)

# Graphique
fig = px.bar(
    top_opportunities,
    x="Opportunity",
    y="Category",
    color="Segment",
    orientation="h",
    title="Catégories avec le plus fort potentiel"
)

st.plotly_chart(fig, use_container_width=True)