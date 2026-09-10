# CA par catégorie
ca_cat = df.groupby('Category')['Revenue'].sum().sort_values(ascending=False)
print(ca_cat)


# CA par marque
ca_brand = df.groupby('Brand')['Revenue'].sum().sort_values(ascending=False)
print(ca_brand)


# Catégories préférées par segment
seg_cat = df.merge(rfm[['Customer_ID', 'Segment']], on='Customer_ID') \
            .groupby(['Segment', 'Category'])['Revenue'].sum().reset_index()
top_cat = seg_cat.sort_values(['Segment', 'Revenue'], ascending=[True, False]) \
                .groupby('Segment').head(3)
print(top_cat)