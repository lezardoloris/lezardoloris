#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { GoogleAdsClient } from './google-ads-client.js';
import { config } from 'dotenv';
import { z } from 'zod';

config();

// Validate environment variables
const envSchema = z.object({
  GOOGLE_ADS_DEVELOPER_TOKEN: z.string(),
  GOOGLE_ADS_CLIENT_ID: z.string(),
  GOOGLE_ADS_CLIENT_SECRET: z.string(),
  GOOGLE_ADS_REFRESH_TOKEN: z.string(),
  GOOGLE_ADS_CUSTOMER_ID: z.string(),
  GOOGLE_ADS_LOGIN_CUSTOMER_ID: z.string().optional(),
});

const env = envSchema.parse(process.env);

// Initialize Google Ads client
const googleAdsClient = new GoogleAdsClient({
  developer_token: env.GOOGLE_ADS_DEVELOPER_TOKEN,
  client_id: env.GOOGLE_ADS_CLIENT_ID,
  client_secret: env.GOOGLE_ADS_CLIENT_SECRET,
  refresh_token: env.GOOGLE_ADS_REFRESH_TOKEN,
  customer_id: env.GOOGLE_ADS_CUSTOMER_ID,
  login_customer_id: env.GOOGLE_ADS_LOGIN_CUSTOMER_ID,
});

// Define available tools
const tools: Tool[] = [
  {
    name: 'get_account_info',
    description: 'Get Google Ads account information including account ID, name, currency, and timezone',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
  {
    name: 'get_campaigns',
    description: 'Retrieve all campaigns with performance metrics including impressions, clicks, cost, conversions, CTR, and average CPC',
    inputSchema: {
      type: 'object',
      properties: {
        date_range: {
          type: 'string',
          description: 'Date range for metrics (e.g., LAST_7_DAYS, LAST_30_DAYS, LAST_90_DAYS, THIS_MONTH, LAST_MONTH)',
          default: 'LAST_30_DAYS',
        },
      },
    },
  },
  {
    name: 'get_ad_groups',
    description: 'Retrieve ad groups with performance metrics. Optionally filter by campaign ID',
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: {
          type: 'string',
          description: 'Optional campaign ID to filter ad groups',
        },
        date_range: {
          type: 'string',
          description: 'Date range for metrics (e.g., LAST_7_DAYS, LAST_30_DAYS, LAST_90_DAYS)',
          default: 'LAST_30_DAYS',
        },
      },
    },
  },
  {
    name: 'get_keywords',
    description: 'Retrieve keywords with performance metrics including quality score. Optionally filter by ad group ID',
    inputSchema: {
      type: 'object',
      properties: {
        ad_group_id: {
          type: 'string',
          description: 'Optional ad group ID to filter keywords',
        },
        date_range: {
          type: 'string',
          description: 'Date range for metrics (e.g., LAST_7_DAYS, LAST_30_DAYS, LAST_90_DAYS)',
          default: 'LAST_30_DAYS',
        },
      },
    },
  },
  {
    name: 'execute_gaql_query',
    description: 'Execute a custom GAQL (Google Ads Query Language) query for advanced reporting and analysis. Use this for complex queries not covered by other tools',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'GAQL query string (e.g., "SELECT campaign.id, campaign.name, metrics.clicks FROM campaign WHERE segments.date DURING LAST_30_DAYS")',
        },
      },
      required: ['query'],
    },
  },
  {
    name: 'create_campaign',
    description: 'Create a new Google Ads campaign with specified name, budget, and bidding strategy',
    inputSchema: {
      type: 'object',
      properties: {
        name: {
          type: 'string',
          description: 'Campaign name',
        },
        budget: {
          type: 'number',
          description: 'Daily budget in account currency',
        },
        bidding_strategy: {
          type: 'string',
          description: 'Bidding strategy type (MAXIMIZE_CONVERSIONS, MAXIMIZE_CLICKS, TARGET_CPA, etc.)',
          default: 'MAXIMIZE_CONVERSIONS',
        },
      },
      required: ['name', 'budget'],
    },
  },
  {
    name: 'update_campaign_status',
    description: 'Update campaign status to ENABLED, PAUSED, or REMOVED',
    inputSchema: {
      type: 'object',
      properties: {
        campaign_id: {
          type: 'string',
          description: 'Campaign ID to update',
        },
        status: {
          type: 'string',
          enum: ['ENABLED', 'PAUSED', 'REMOVED'],
          description: 'New campaign status',
        },
      },
      required: ['campaign_id', 'status'],
    },
  },
  {
    name: 'add_keywords',
    description: 'Add keywords to an ad group with specified match types and optional CPC bids',
    inputSchema: {
      type: 'object',
      properties: {
        ad_group_id: {
          type: 'string',
          description: 'Ad group ID to add keywords to',
        },
        keywords: {
          type: 'array',
          description: 'Array of keywords to add',
          items: {
            type: 'object',
            properties: {
              text: {
                type: 'string',
                description: 'Keyword text',
              },
              match_type: {
                type: 'string',
                enum: ['EXACT', 'PHRASE', 'BROAD'],
                description: 'Keyword match type',
              },
              cpc_bid: {
                type: 'number',
                description: 'Optional CPC bid in account currency',
              },
            },
            required: ['text', 'match_type'],
          },
        },
      },
      required: ['ad_group_id', 'keywords'],
    },
  },
  {
    name: 'analyze_campaign_performance',
    description: 'Analyze campaign performance and identify opportunities for optimization. Returns campaigns sorted by ROAS or other metrics with actionable insights',
    inputSchema: {
      type: 'object',
      properties: {
        date_range: {
          type: 'string',
          description: 'Date range for analysis (e.g., LAST_30_DAYS)',
          default: 'LAST_30_DAYS',
        },
        min_roas: {
          type: 'number',
          description: 'Minimum ROAS threshold to identify underperforming campaigns',
          default: 2,
        },
      },
    },
  },
];

// Create MCP server
const server = new Server(
  {
    name: 'google-ads-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Handle tool list requests
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools };
});

// Handle tool execution requests
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'get_account_info': {
        const info = await googleAdsClient.getAccountInfo();
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(info, null, 2),
            },
          ],
        };
      }

      case 'get_campaigns': {
        const dateRange = (args?.date_range as string) || 'LAST_30_DAYS';
        const campaigns = await googleAdsClient.getCampaigns(dateRange);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(campaigns, null, 2),
            },
          ],
        };
      }

      case 'get_ad_groups': {
        const campaignId = args?.campaign_id as string | undefined;
        const dateRange = (args?.date_range as string) || 'LAST_30_DAYS';
        const adGroups = await googleAdsClient.getAdGroups(campaignId, dateRange);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(adGroups, null, 2),
            },
          ],
        };
      }

      case 'get_keywords': {
        const adGroupId = args?.ad_group_id as string | undefined;
        const dateRange = (args?.date_range as string) || 'LAST_30_DAYS';
        const keywords = await googleAdsClient.getKeywords(adGroupId, dateRange);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(keywords, null, 2),
            },
          ],
        };
      }

      case 'execute_gaql_query': {
        const query = args?.query as string;
        if (!query) {
          throw new Error('query parameter is required');
        }
        const result = await googleAdsClient.executeGAQLQuery(query);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case 'create_campaign': {
        const name = args?.name as string;
        const budget = args?.budget as number;
        const biddingStrategy = (args?.bidding_strategy as string) || 'MAXIMIZE_CONVERSIONS';

        if (!name || !budget) {
          throw new Error('name and budget parameters are required');
        }

        const campaignId = await googleAdsClient.createCampaign(name, budget, biddingStrategy);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ success: true, campaign_id: campaignId }, null, 2),
            },
          ],
        };
      }

      case 'update_campaign_status': {
        const campaignId = args?.campaign_id as string;
        const status = args?.status as 'ENABLED' | 'PAUSED' | 'REMOVED';

        if (!campaignId || !status) {
          throw new Error('campaign_id and status parameters are required');
        }

        await googleAdsClient.updateCampaignStatus(campaignId, status);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ success: true, message: `Campaign ${campaignId} status updated to ${status}` }, null, 2),
            },
          ],
        };
      }

      case 'add_keywords': {
        const adGroupId = args?.ad_group_id as string;
        const keywords = args?.keywords as Array<{ text: string; match_type: string; cpc_bid?: number }>;

        if (!adGroupId || !keywords) {
          throw new Error('ad_group_id and keywords parameters are required');
        }

        await googleAdsClient.addKeywords(
          adGroupId,
          keywords.map(k => ({ text: k.text, matchType: k.match_type, cpcBid: k.cpc_bid }))
        );

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ success: true, message: `Added ${keywords.length} keywords to ad group ${adGroupId}` }, null, 2),
            },
          ],
        };
      }

      case 'analyze_campaign_performance': {
        const dateRange = (args?.date_range as string) || 'LAST_30_DAYS';
        const minRoas = (args?.min_roas as number) || 2;

        const campaigns = await googleAdsClient.getCampaigns(dateRange);

        // Calculate ROAS and identify underperforming campaigns
        const analysis = campaigns.map(campaign => {
          const roas = campaign.conversions && campaign.cost ? (campaign.conversions * 50) / campaign.cost : 0; // Assuming $50 per conversion
          const isUnderperforming = roas < minRoas && campaign.cost > 100;

          return {
            ...campaign,
            roas: roas.toFixed(2),
            isUnderperforming,
            recommendation: isUnderperforming
              ? 'Consider pausing or optimizing this campaign'
              : 'Campaign is performing well',
          };
        });

        // Sort by ROAS ascending to show worst performers first
        analysis.sort((a, b) => parseFloat(a.roas) - parseFloat(b.roas));

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                summary: {
                  total_campaigns: campaigns.length,
                  underperforming_campaigns: analysis.filter(c => c.isUnderperforming).length,
                  total_spend: campaigns.reduce((sum, c) => sum + (c.cost || 0), 0).toFixed(2),
                  total_conversions: campaigns.reduce((sum, c) => sum + (c.conversions || 0), 0),
                },
                campaigns: analysis,
              }, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ error: errorMessage }, null, 2),
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Google Ads MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
