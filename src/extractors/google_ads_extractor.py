"""
Google Ads Data Extractor

Extraction données Google Ads via API
Connexion avec MCP pour analyse
"""

from google.ads.googleads.client import GoogleAdsClient
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoogleAdsExtractor:
    """Extract data from Google Ads API for analysis"""

    def __init__(self, credentials_path: str, customer_id: str):
        """
        Initialize Google Ads Extractor

        Args:
            credentials_path: Path to Google Ads API credentials (YAML)
            customer_id: Google Ads customer ID (without hyphens)
        """
        try:
            self.client = GoogleAdsClient.load_from_storage(credentials_path)
            self.customer_id = customer_id
            logger.info(f"Successfully initialized for customer ID: {customer_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Google Ads client: {e}")
            raise

    def extract_campaign_data(self, date_range_days: int = 30) -> List[Dict]:
        """
        Extract last X days of campaign performance

        Args:
            date_range_days: Number of days to extract (default: 30)

        Returns:
            List of campaign performance dictionaries
        """
        logger.info(f"Extracting campaign data for last {date_range_days} days")

        ga_service = self.client.get_service("GoogleAdsService")

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=date_range_days)

        query = f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.cost_per_conversion
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND metrics.impressions > 0
        ORDER BY metrics.cost_micros DESC
        """

        try:
            results = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )

            campaigns = []
            for batch in results:
                for row in batch.results:
                    cost = row.metrics.cost_micros / 1_000_000
                    conv_value = row.metrics.conversions_value

                    campaigns.append({
                        'id': row.campaign.id,
                        'name': row.campaign.name,
                        'status': row.campaign.status.name,
                        'channel_type': row.campaign.advertising_channel_type.name,
                        'bid_strategy': row.campaign.bidding_strategy_type.name,
                        'impressions': row.metrics.impressions,
                        'clicks': row.metrics.clicks,
                        'ctr': row.metrics.ctr,
                        'avg_cpc': row.metrics.average_cpc / 1_000_000,
                        'cost': cost,
                        'conversions': row.metrics.conversions,
                        'conversion_value': conv_value,
                        'cost_per_conversion': row.metrics.cost_per_conversion / 1_000_000 if row.metrics.conversions > 0 else 0,
                        'roas': conv_value / cost if cost > 0 else 0
                    })

            logger.info(f"Extracted {len(campaigns)} campaigns")
            return campaigns

        except Exception as e:
            logger.error(f"Failed to extract campaign data: {e}")
            raise

    def extract_keyword_data(self, limit: int = 500) -> List[Dict]:
        """
        Extract keyword performance with quality score

        Args:
            limit: Maximum number of keywords to extract

        Returns:
            List of keyword performance dictionaries
        """
        logger.info(f"Extracting top {limit} keywords")

        ga_service = self.client.get_service("GoogleAdsService")

        query = f"""
        SELECT
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.quality_info.quality_score,
            ad_group_criterion.final_urls,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM keyword_view
        WHERE metrics.impressions > 0
        AND ad_group_criterion.status = 'ENABLED'
        ORDER BY metrics.cost_micros DESC
        LIMIT {limit}
        """

        try:
            results = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )

            keywords = []
            for batch in results:
                for row in batch.results:
                    cost = row.metrics.cost_micros / 1_000_000
                    conv_value = row.metrics.conversions_value

                    keywords.append({
                        'campaign_id': row.campaign.id,
                        'campaign_name': row.campaign.name,
                        'ad_group_id': row.ad_group.id,
                        'ad_group_name': row.ad_group.name,
                        'keyword': row.ad_group_criterion.keyword.text,
                        'match_type': row.ad_group_criterion.keyword.match_type.name,
                        'quality_score': row.ad_group_criterion.quality_info.quality_score if hasattr(row.ad_group_criterion.quality_info, 'quality_score') else None,
                        'impressions': row.metrics.impressions,
                        'clicks': row.metrics.clicks,
                        'ctr': row.metrics.ctr,
                        'avg_cpc': row.metrics.average_cpc / 1_000_000,
                        'cost': cost,
                        'conversions': row.metrics.conversions,
                        'conversion_value': conv_value,
                        'roas': conv_value / cost if cost > 0 else 0
                    })

            logger.info(f"Extracted {len(keywords)} keywords")
            return keywords

        except Exception as e:
            logger.error(f"Failed to extract keyword data: {e}")
            raise

    def extract_shopping_data(self, limit: int = 1000) -> List[Dict]:
        """
        Extract Shopping campaign product performance

        Args:
            limit: Maximum number of products to extract

        Returns:
            List of product performance dictionaries
        """
        logger.info(f"Extracting Shopping product performance")

        ga_service = self.client.get_service("GoogleAdsService")

        query = f"""
        SELECT
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            segments.product_item_id,
            segments.product_title,
            segments.product_type_l1,
            segments.product_type_l2,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM shopping_performance_view
        WHERE metrics.impressions > 0
        ORDER BY metrics.cost_micros DESC
        LIMIT {limit}
        """

        try:
            results = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )

            products = []
            for batch in results:
                for row in batch.results:
                    cost = row.metrics.cost_micros / 1_000_000
                    conv_value = row.metrics.conversions_value

                    products.append({
                        'campaign_id': row.campaign.id,
                        'campaign_name': row.campaign.name,
                        'ad_group_id': row.ad_group.id,
                        'ad_group_name': row.ad_group.name,
                        'product_id': row.segments.product_item_id,
                        'product_title': row.segments.product_title,
                        'product_category_l1': row.segments.product_type_l1,
                        'product_category_l2': row.segments.product_type_l2,
                        'impressions': row.metrics.impressions,
                        'clicks': row.metrics.clicks,
                        'ctr': row.metrics.ctr,
                        'avg_cpc': row.metrics.average_cpc / 1_000_000,
                        'cost': cost,
                        'conversions': row.metrics.conversions,
                        'conversion_value': conv_value,
                        'roas': conv_value / cost if cost > 0 else 0
                    })

            logger.info(f"Extracted {len(products)} products")
            return products

        except Exception as e:
            logger.error(f"Failed to extract Shopping data: {e}")
            raise

    def extract_search_terms(self, limit: int = 500) -> List[Dict]:
        """
        Extract search terms report (actual user queries)

        Args:
            limit: Maximum number of search terms to extract

        Returns:
            List of search term performance dictionaries
        """
        logger.info(f"Extracting search terms")

        ga_service = self.client.get_service("GoogleAdsService")

        query = f"""
        SELECT
            campaign.name,
            ad_group.name,
            segments.search_term_match_type,
            search_term_view.search_term,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value
        FROM search_term_view
        WHERE metrics.impressions > 0
        ORDER BY metrics.impressions DESC
        LIMIT {limit}
        """

        try:
            results = ga_service.search_stream(
                customer_id=self.customer_id,
                query=query
            )

            search_terms = []
            for batch in results:
                for row in batch.results:
                    cost = row.metrics.cost_micros / 1_000_000
                    conv_value = row.metrics.conversions_value

                    search_terms.append({
                        'campaign_name': row.campaign.name,
                        'ad_group_name': row.ad_group.name,
                        'search_term': row.search_term_view.search_term,
                        'match_type': row.segments.search_term_match_type.name,
                        'impressions': row.metrics.impressions,
                        'clicks': row.metrics.clicks,
                        'ctr': row.metrics.ctr,
                        'avg_cpc': row.metrics.average_cpc / 1_000_000,
                        'cost': cost,
                        'conversions': row.metrics.conversions,
                        'conversion_value': conv_value,
                        'roas': conv_value / cost if cost > 0 else 0
                    })

            logger.info(f"Extracted {len(search_terms)} search terms")
            return search_terms

        except Exception as e:
            logger.error(f"Failed to extract search terms: {e}")
            raise

    def extract_all_data(self, date_range_days: int = 30) -> Dict:
        """
        Extract all data types in one call

        Args:
            date_range_days: Number of days to extract

        Returns:
            Dictionary with all extracted data
        """
        logger.info("Starting full data extraction")

        data = {
            'metadata': {
                'customer_id': self.customer_id,
                'extraction_date': datetime.now().isoformat(),
                'date_range_days': date_range_days,
                'start_date': (datetime.now().date() - timedelta(days=date_range_days)).isoformat(),
                'end_date': datetime.now().date().isoformat()
            },
            'campaigns': self.extract_campaign_data(date_range_days),
            'keywords': self.extract_keyword_data(),
            'products': self.extract_shopping_data(),
            'search_terms': self.extract_search_terms()
        }

        logger.info("Full data extraction complete")
        return data

    def export_to_json(self, data: Dict, output_path: str = "google_ads_data.json"):
        """
        Export extracted data to JSON file

        Args:
            data: Data dictionary to export
            output_path: Path to output JSON file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data exported to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            raise


# Usage Example
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python google_ads_extractor.py <credentials_path> <customer_id>")
        print("Example: python google_ads_extractor.py google-ads.yaml 1234567890")
        sys.exit(1)

    credentials_path = sys.argv[1]
    customer_id = sys.argv[2]

    try:
        extractor = GoogleAdsExtractor(credentials_path, customer_id)

        # Extract all data
        data = extractor.extract_all_data(date_range_days=30)

        # Export to JSON
        extractor.export_to_json(data, "google_ads_data.json")

        print(f"\n✅ Extraction complete!")
        print(f"   Campaigns: {len(data['campaigns'])}")
        print(f"   Keywords: {len(data['keywords'])}")
        print(f"   Products: {len(data['products'])}")
        print(f"   Search Terms: {len(data['search_terms'])}")
        print(f"\n📊 Data exported to: google_ads_data.json")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
