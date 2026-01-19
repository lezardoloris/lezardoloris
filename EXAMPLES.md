# Google Ads MCP Server - Example Prompts

This document contains example prompts you can use with Claude AI once the Google Ads MCP server is connected.

## Basic Account Information

### Get Account Overview
```
What's my Google Ads account information?
```

### Check Daily Spend
```
How much did I spend on Google Ads yesterday?
```

## Campaign Analysis

### List All Campaigns
```
Show me all my campaigns from the last 30 days with their performance metrics
```

### Top Performing Campaigns
```
Which campaigns had the most conversions in the last month?
```

### Budget Analysis
```
Show me campaigns spending over $500 in the last 30 days, sorted by spend
```

### Low Performing Campaigns
```
Find campaigns wasting budget - show me campaigns with:
- ROAS below 2x
- Spend over $100
- Less than 5 conversions
```

## Ad Group & Keyword Analysis

### Ad Groups by Campaign
```
Show me all ad groups in campaign 123456789 with performance data
```

### Top Keywords
```
What are my top 20 keywords by conversions in the last 30 days?
```

### Poor Quality Keywords
```
Show me keywords with quality score below 5 that have spent more than $50
```

### High Cost Keywords
```
List keywords with cost per conversion above $20
```

## Comprehensive Audits

### Full Account Audit
```
Generate a comprehensive Google Ads audit for the last 30 days including:
1. Account overview and total spend
2. Campaign performance ranked by ROAS
3. Top and bottom performing ad groups
4. Keyword analysis with quality scores
5. Identification of budget waste
6. Specific recommendations to improve performance and reduce wasted spend
```

### Campaign Deep Dive
```
Analyze campaign 123456789 in detail:
- Overall performance metrics
- All ad groups with their performance
- Top 50 keywords
- Quality score distribution
- Recommendations for optimization
```

### Search Terms Analysis
```
Execute this GAQL query to get search terms:
SELECT
  segments.search_term_view_search_term,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
AND metrics.impressions > 10
ORDER BY metrics.cost_micros DESC
LIMIT 100
```

## Performance Optimization

### ROAS Analysis
```
Analyze all my campaigns and identify which ones have ROAS below 3x in the last 30 days
```

### CTR Analysis
```
Show me campaigns with CTR below 2% that have over 1000 impressions
```

### Budget Reallocation
```
Compare all campaigns by ROAS and recommend which campaigns to increase/decrease budget on
```

### Impression Share
```
Execute this query to check impression share:
SELECT
  campaign.name,
  metrics.search_impression_share,
  metrics.search_budget_lost_impression_share,
  metrics.search_rank_lost_impression_share
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
```

## Campaign Management

### Create New Campaign
```
Create a new Google Ads campaign with these details:
- Name: "Black Friday Sale 2024"
- Daily budget: $200
- Bidding strategy: MAXIMIZE_CONVERSIONS
```

### Pause Underperforming Campaign
```
Pause campaign 987654321 as it's not performing well
```

### Enable Campaign
```
Enable campaign 123456789 to start showing ads
```

## Keyword Management

### Add Keywords
```
Add these keywords to ad group 111222333:
- "best running shoes" - phrase match, $2 CPC bid
- "nike running shoes" - exact match, $2.50 CPC bid
- "running shoes online" - broad match, $1.50 CPC bid
```

### Negative Keywords
```
Show me search terms that should be added as negative keywords - terms with:
- More than 10 clicks
- Zero conversions
- Cost over $50
```

## Geographic Performance

### Location Analysis
```
Execute this query to analyze performance by location:
SELECT
  geographic_view.country_criterion_id,
  geographic_view.location_type,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions
FROM geographic_view
WHERE segments.date DURING LAST_30_DAYS
AND metrics.impressions > 100
ORDER BY metrics.cost_micros DESC
```

## Device Performance

### Device Breakdown
```
Show me performance by device type:
SELECT
  segments.device,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.ctr
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
GROUP BY segments.device
```

## Time-Based Analysis

### Day of Week Performance
```
Analyze performance by day of week:
SELECT
  segments.day_of_week,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
GROUP BY segments.day_of_week
ORDER BY segments.day_of_week
```

### Week over Week Comparison
```
Compare performance between last week and the week before:
- Show total spend, conversions, and ROAS for each week
- Identify which campaigns improved or declined
```

## Advanced GAQL Queries

### Shopping Campaign Analysis
```
Execute this query for shopping campaigns:
SELECT
  campaign.name,
  segments.product_title,
  segments.product_item_id,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions
FROM shopping_performance_view
WHERE segments.date DURING LAST_30_DAYS
AND campaign.advertising_channel_type = 'SHOPPING'
ORDER BY metrics.cost_micros DESC
LIMIT 100
```

### Ad Performance
```
Get detailed ad performance:
SELECT
  ad_group_ad.ad.id,
  ad_group_ad.ad.final_urls,
  ad_group_ad.ad.responsive_search_ad.headlines,
  ad_group_ad.ad.responsive_search_ad.descriptions,
  metrics.impressions,
  metrics.clicks,
  metrics.ctr,
  metrics.conversions
FROM ad_group_ad
WHERE segments.date DURING LAST_30_DAYS
AND ad_group_ad.status = 'ENABLED'
ORDER BY metrics.impressions DESC
LIMIT 50
```

## Reporting & Insights

### Executive Summary
```
Create an executive summary of my Google Ads performance for the last month:
- Total spend, impressions, clicks, conversions
- Average CPC, CTR, conversion rate
- Top 5 campaigns by conversions
- Bottom 5 campaigns by ROAS
- 3 key recommendations for optimization
```

### Weekly Report
```
Generate a weekly performance report:
- Week over week change in key metrics
- New campaigns or major changes
- Campaigns that need attention
- Quick wins and opportunities
```

### Budget Pacing
```
Check if we're on pace with our monthly budget:
- Calculate daily spend for the last 7 days
- Project end-of-month spend
- Compare to monthly budget target
```

## Custom Audiences & Targeting

### Audience Performance
```
Execute this query to see audience performance:
SELECT
  campaign.name,
  ad_group.name,
  ad_group_criterion.user_list.user_list,
  metrics.impressions,
  metrics.clicks,
  metrics.conversions
FROM user_location_view
WHERE segments.date DURING LAST_30_DAYS
```

## Competitive Analysis

### Auction Insights
```
Show me auction insights data:
SELECT
  segments.auction_insight_domain,
  metrics.impression_reach,
  metrics.overlap_rate,
  metrics.position_above_rate
FROM auction_insight_search_term_view
WHERE segments.date DURING LAST_30_DAYS
```

## Tips for Using These Prompts

1. **Replace IDs**: Update campaign, ad group, and keyword IDs with your actual IDs
2. **Adjust Date Ranges**: Change date ranges to match your needs (LAST_7_DAYS, LAST_90_DAYS, etc.)
3. **Customize Thresholds**: Modify spend, ROAS, and other thresholds based on your goals
4. **Combine Queries**: Ask Claude to run multiple analyses and synthesize insights
5. **Follow Up**: Ask clarifying questions or request deeper analysis on specific findings

## Pro Tips

- Start with broad questions, then drill down into specific areas
- Ask Claude to explain the metrics if you're unfamiliar with them
- Request visualizations or formatted tables for easier reading
- Combine multiple tools (campaigns + keywords + ad groups) for comprehensive analysis
- Use GAQL for very specific queries that aren't covered by standard tools

---

**Need help?** Ask Claude "What can you help me analyze with my Google Ads data?"
