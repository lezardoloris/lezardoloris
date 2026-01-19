export interface GoogleAdsConfig {
  developer_token: string;
  client_id: string;
  client_secret: string;
  refresh_token: string;
  customer_id: string;
  login_customer_id?: string;
}

export interface CampaignData {
  id: string;
  name: string;
  status: string;
  budget?: number;
  impressions?: number;
  clicks?: number;
  cost?: number;
  conversions?: number;
  ctr?: number;
  avgCpc?: number;
  conversionRate?: number;
}

export interface AdGroupData {
  id: string;
  name: string;
  campaignId: string;
  campaignName: string;
  status: string;
  cpcBid?: number;
  impressions?: number;
  clicks?: number;
  cost?: number;
  conversions?: number;
}

export interface KeywordData {
  id: string;
  text: string;
  matchType: string;
  adGroupId: string;
  adGroupName: string;
  campaignId: string;
  campaignName: string;
  status: string;
  impressions?: number;
  clicks?: number;
  cost?: number;
  conversions?: number;
  ctr?: number;
  qualityScore?: number;
}

export interface GAQLQueryResult {
  fields: string[];
  rows: any[];
}
