marketing['CTR'] = marketing['Clicks'] / marketing['Impressions']
marketing['CVR'] = marketing['Conversions'] / marketing['Clicks']
marketing['CPC'] = marketing['Budget'] / marketing['Clicks']
marketing['CPA'] = marketing['Budget'] / marketing['Conversions']

# AOV global (panier moyen)
aov = df['Revenue'].mean()
marketing['ROAS_est'] = (marketing['Conversions'] * aov) / marketing['Budget']

# Agrégation par canal
campaign_channel = marketing.groupby('Channel').agg({
    'Budget': 'sum',
    'Impressions': 'sum',
    'Clicks': 'sum',
    'Conversions': 'sum'
}).reset_index()

campaign_channel['CTR'] = campaign_channel['Clicks'] / campaign_channel['Impressions']
campaign_channel['CVR'] = campaign_channel['Conversions'] / campaign_channel['Clicks']
campaign_channel['CPA'] = campaign_channel['Budget'] / campaign_channel['Conversions']
campaign_channel['ROAS_est'] = (campaign_channel['Conversions'] * aov) / campaign_channel['Budget']

print(campaign_channel.sort_values('ROAS_est', ascending=False))