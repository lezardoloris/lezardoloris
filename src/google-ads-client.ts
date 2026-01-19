import { GoogleAdsApi, Customer } from 'google-ads-api';
import type { GoogleAdsConfig, CampaignData, AdGroupData, KeywordData, GAQLQueryResult } from './types.js';

export class GoogleAdsClient {
  private client: GoogleAdsApi;
  private customer: Customer;
  private config: GoogleAdsConfig;

  constructor(config: GoogleAdsConfig) {
    this.config = config;

    this.client = new GoogleAdsApi({
      client_id: config.client_id,
      client_secret: config.client_secret,
      developer_token: config.developer_token,
    });

    this.customer = this.client.Customer({
      customer_id: config.customer_id,
      refresh_token: config.refresh_token,
      login_customer_id: config.login_customer_id,
    });
  }

  async getCampaigns(dateRange: string = 'LAST_30_DAYS'): Promise<CampaignData[]> {
    const query = `
      SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign_budget.amount_micros,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr,
        metrics.average_cpc
      FROM campaign
      WHERE segments.date DURING ${dateRange}
      ORDER BY metrics.impressions DESC
    `;

    const result = await this.customer.query(query);

    return result.map((row: any) => ({
      id: row.campaign?.id?.toString() || '',
      name: row.campaign?.name || '',
      status: row.campaign?.status || '',
      budget: row.campaign_budget?.amount_micros ? row.campaign_budget.amount_micros / 1_000_000 : undefined,
      impressions: row.metrics?.impressions || 0,
      clicks: row.metrics?.clicks || 0,
      cost: row.metrics?.cost_micros ? row.metrics.cost_micros / 1_000_000 : 0,
      conversions: row.metrics?.conversions || 0,
      ctr: row.metrics?.ctr || 0,
      avgCpc: row.metrics?.average_cpc ? row.metrics.average_cpc / 1_000_000 : 0,
    }));
  }

  async getAdGroups(campaignId?: string, dateRange: string = 'LAST_30_DAYS'): Promise<AdGroupData[]> {
    let query = `
      SELECT
        ad_group.id,
        ad_group.name,
        ad_group.campaign,
        ad_group.status,
        ad_group.cpc_bid_micros,
        campaign.id,
        campaign.name,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions
      FROM ad_group
      WHERE segments.date DURING ${dateRange}
    `;

    if (campaignId) {
      query += ` AND campaign.id = ${campaignId}`;
    }

    query += ` ORDER BY metrics.impressions DESC`;

    const result = await this.customer.query(query);

    return result.map((row: any) => ({
      id: row.ad_group?.id?.toString() || '',
      name: row.ad_group?.name || '',
      campaignId: row.campaign?.id?.toString() || '',
      campaignName: row.campaign?.name || '',
      status: row.ad_group?.status || '',
      cpcBid: row.ad_group?.cpc_bid_micros ? row.ad_group.cpc_bid_micros / 1_000_000 : undefined,
      impressions: row.metrics?.impressions || 0,
      clicks: row.metrics?.clicks || 0,
      cost: row.metrics?.cost_micros ? row.metrics.cost_micros / 1_000_000 : 0,
      conversions: row.metrics?.conversions || 0,
    }));
  }

  async getKeywords(adGroupId?: string, dateRange: string = 'LAST_30_DAYS'): Promise<KeywordData[]> {
    let query = `
      SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        ad_group_criterion.criterion_id,
        ad_group_criterion.status,
        ad_group.id,
        ad_group.name,
        campaign.id,
        campaign.name,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr,
        ad_group_criterion.quality_info.quality_score
      FROM keyword_view
      WHERE segments.date DURING ${dateRange}
    `;

    if (adGroupId) {
      query += ` AND ad_group.id = ${adGroupId}`;
    }

    query += ` ORDER BY metrics.impressions DESC LIMIT 1000`;

    const result = await this.customer.query(query);

    return result.map((row: any) => ({
      id: row.ad_group_criterion?.criterion_id?.toString() || '',
      text: row.ad_group_criterion?.keyword?.text || '',
      matchType: row.ad_group_criterion?.keyword?.match_type || '',
      adGroupId: row.ad_group?.id?.toString() || '',
      adGroupName: row.ad_group?.name || '',
      campaignId: row.campaign?.id?.toString() || '',
      campaignName: row.campaign?.name || '',
      status: row.ad_group_criterion?.status || '',
      impressions: row.metrics?.impressions || 0,
      clicks: row.metrics?.clicks || 0,
      cost: row.metrics?.cost_micros ? row.metrics.cost_micros / 1_000_000 : 0,
      conversions: row.metrics?.conversions || 0,
      ctr: row.metrics?.ctr || 0,
      qualityScore: row.ad_group_criterion?.quality_info?.quality_score || 0,
    }));
  }

  async executeGAQLQuery(query: string): Promise<GAQLQueryResult> {
    const result = await this.customer.query(query);

    if (result.length === 0) {
      return { fields: [], rows: [] };
    }

    // Extract field names from the first row
    const fields = Object.keys(result[0]);

    return {
      fields,
      rows: result,
    };
  }

  async createCampaign(name: string, budget: number, biddingStrategy: string = 'MAXIMIZE_CONVERSIONS'): Promise<string> {
    // First create a budget
    const budgetResourceName = await this.customer.campaignBudgets.create({
      name: `Budget for ${name}`,
      amount_micros: budget * 1_000_000,
      delivery_method: 'STANDARD',
    });

    // Then create the campaign
    const campaign = await this.customer.campaigns.create({
      name,
      campaign_budget: budgetResourceName,
      advertising_channel_type: 'SEARCH',
      status: 'PAUSED',
      bidding_strategy_type: biddingStrategy,
    });

    return campaign;
  }

  async updateCampaignStatus(campaignId: string, status: 'ENABLED' | 'PAUSED' | 'REMOVED'): Promise<void> {
    await this.customer.campaigns.update({
      resource_name: `customers/${this.config.customer_id}/campaigns/${campaignId}`,
      status,
    });
  }

  async addKeywords(adGroupId: string, keywords: Array<{ text: string; matchType: string; cpcBid?: number }>): Promise<void> {
    const operations = keywords.map(keyword => ({
      ad_group: `customers/${this.config.customer_id}/adGroups/${adGroupId}`,
      keyword: {
        text: keyword.text,
        match_type: keyword.matchType,
      },
      status: 'ENABLED',
      cpc_bid_micros: keyword.cpcBid ? keyword.cpcBid * 1_000_000 : undefined,
    }));

    await this.customer.adGroupCriteria.create(operations);
  }

  async getAccountInfo(): Promise<any> {
    const query = `
      SELECT
        customer.id,
        customer.descriptive_name,
        customer.currency_code,
        customer.time_zone,
        customer.manager
      FROM customer
      LIMIT 1
    `;

    const result = await this.customer.query(query);
    return result[0];
  }
}
