

#  % de clients du segment qui achètent la catégorie


seg_cat_clients = df.merge(rfm[['Customer_ID', 'Segment']], on='Customer_ID') \
    .groupby(['Segment', 'Category'])['Customer_ID'].nunique().reset_index(name='NbClients')

seg_size = rfm.groupby('Segment')['Customer_ID'].count().reset_index(name='SegmentSize')

opp = seg_cat.merge(seg_cat_clients, on=['Segment', 'Category']) \
             .merge(seg_size, on='Segment')
opp['Part'] = opp.groupby('Segment')['Revenue'].transform(lambda x: x / x.sum())
opp['Penetration'] = opp['NbClients'] / opp['SegmentSize']
opp['Opportunity'] = opp['Part'] * (1 - opp['Penetration'])

print(opp.sort_values('Opportunity', ascending=False).head(10))