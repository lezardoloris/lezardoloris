"""
Google Keyword Planner Integration

Intégration Google Keyword Planner + Trends
Pour analyse marché et volume recherche
"""

from google.ads.googleads.client import GoogleAdsClient
from typing import List, Dict, Optional
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KeywordPlannerAnalyzer:
    """Analyze keyword opportunities using Google Keyword Planner"""

    # Common location IDs (geo_target_constants)
    LOCATION_IDS = {
        'france': '2250',
        'paris': '1006094',
        'belgium': '2056',
        'switzerland': '2756',
        'canada': '2124',
        'us': '2840',
        'uk': '2826',
        'germany': '2276',
        'spain': '2724',
        'italy': '2380'
    }

    # Language constants
    LANGUAGE_IDS = {
        'french': '1002',
        'english': '1000',
        'german': '1001',
        'spanish': '1003',
        'italian': '1004'
    }

    def __init__(self, credentials_path: str, customer_id: str):
        """
        Initialize Keyword Planner Analyzer

        Args:
            credentials_path: Path to Google Ads API credentials
            customer_id: Google Ads customer ID
        """
        try:
            self.client = GoogleAdsClient.load_from_storage(credentials_path)
            self.customer_id = customer_id
            logger.info(f"Keyword Planner initialized for customer {customer_id}")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            raise

    def get_keyword_ideas(
        self,
        seed_keywords: List[str],
        location_names: List[str] = None,
        language: str = 'french'
    ) -> List[Dict]:
        """
        Get keyword ideas based on seed keywords

        Args:
            seed_keywords: List of seed keywords to expand
            location_names: List of location names (e.g., ['france', 'belgium'])
            language: Language for keywords (default: 'french')

        Returns:
            List of keyword ideas with metrics
        """
        logger.info(f"Getting keyword ideas for: {seed_keywords}")

        # Default to France if no location specified
        if not location_names:
            location_names = ['france']

        # Convert location names to IDs
        location_ids = []
        for loc in location_names:
            loc_lower = loc.lower()
            if loc_lower in self.LOCATION_IDS:
                location_ids.append(self.LOCATION_IDS[loc_lower])
            else:
                logger.warning(f"Unknown location: {loc}")

        if not location_ids:
            raise ValueError("No valid locations specified")

        # Get language ID
        language_id = self.LANGUAGE_IDS.get(language.lower(), '1002')  # Default to French

        keyword_plan_idea_service = self.client.get_service("KeywordPlanIdeaService")

        # Build request
        request = self.client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = self.customer_id

        # Set location
        for location_id in location_ids:
            request.geo_target_constants.append(
                f"geoTargetConstants/{location_id}"
            )

        # Set language
        request.language = f"languageConstants/{language_id}"

        # Include adult keywords or not
        request.include_adult_keywords = False

        # Keyword seed
        request.keyword_seed.keywords.extend(seed_keywords)

        try:
            response = keyword_plan_idea_service.generate_keyword_ideas(request=request)

            keyword_ideas = []
            for idea in response.results:
                metrics = idea.keyword_idea_metrics

                # Competition level
                competition = metrics.competition.name if hasattr(metrics, 'competition') else 'UNKNOWN'

                # CPC range
                low_cpc = metrics.low_top_of_page_bid_micros / 1_000_000 if metrics.low_top_of_page_bid_micros else 0
                high_cpc = metrics.high_top_of_page_bid_micros / 1_000_000 if metrics.high_top_of_page_bid_micros else 0
                avg_cpc = (low_cpc + high_cpc) / 2 if (low_cpc or high_cpc) else 0

                keyword_ideas.append({
                    'keyword': idea.text,
                    'avg_monthly_searches': metrics.avg_monthly_searches,
                    'competition': competition,
                    'competition_index': metrics.competition_index if hasattr(metrics, 'competition_index') else None,
                    'low_cpc_eur': round(low_cpc, 2),
                    'high_cpc_eur': round(high_cpc, 2),
                    'avg_cpc_eur': round(avg_cpc, 2)
                })

            # Sort by search volume
            keyword_ideas.sort(key=lambda x: x['avg_monthly_searches'], reverse=True)

            logger.info(f"Retrieved {len(keyword_ideas)} keyword ideas")
            return keyword_ideas

        except Exception as e:
            logger.error(f"Failed to get keyword ideas: {e}")
            raise

    def analyze_market_volume(
        self,
        primary_keywords: List[str],
        location_names: List[str] = None,
        language: str = 'french'
    ) -> Dict:
        """
        Analyze total addressable market volume

        Args:
            primary_keywords: Primary keywords to analyze
            location_names: Target locations
            language: Target language

        Returns:
            Market analysis dictionary
        """
        logger.info("Analyzing market volume")

        keyword_ideas = self.get_keyword_ideas(primary_keywords, location_names, language)

        if not keyword_ideas:
            return {
                'error': 'No keyword data retrieved',
                'keywords_analyzed': 0
            }

        total_monthly_searches = sum(kw['avg_monthly_searches'] for kw in keyword_ideas)

        # Calculate weighted average CPC
        total_volume = sum(kw['avg_monthly_searches'] for kw in keyword_ideas if kw['avg_monthly_searches'] > 0)
        weighted_cpc = 0

        if total_volume > 0:
            for kw in keyword_ideas:
                if kw['avg_monthly_searches'] > 0:
                    weight = kw['avg_monthly_searches'] / total_volume
                    weighted_cpc += kw['avg_cpc_eur'] * weight

        # Estimate market opportunity
        # Assuming 30% impression share and 4% CTR
        estimated_monthly_clicks = total_monthly_searches * 0.30 * 0.04
        market_opportunity_monthly = estimated_monthly_clicks * weighted_cpc
        market_opportunity_annual = market_opportunity_monthly * 12

        # Competition analysis
        competition_breakdown = {
            'LOW': 0,
            'MEDIUM': 0,
            'HIGH': 0,
            'UNKNOWN': 0
        }

        for kw in keyword_ideas:
            comp = kw.get('competition', 'UNKNOWN')
            competition_breakdown[comp] = competition_breakdown.get(comp, 0) + 1

        # Segment keywords
        high_volume = [kw for kw in keyword_ideas if kw['avg_monthly_searches'] >= 1000]
        medium_volume = [kw for kw in keyword_ideas if 100 <= kw['avg_monthly_searches'] < 1000]
        low_volume = [kw for kw in keyword_ideas if kw['avg_monthly_searches'] < 100]

        analysis = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'locations': location_names or ['france'],
                'language': language,
                'seed_keywords': primary_keywords
            },
            'summary': {
                'keywords_analyzed': len(keyword_ideas),
                'total_monthly_searches': total_monthly_searches,
                'weighted_avg_cpc': round(weighted_cpc, 2),
                'estimated_monthly_clicks': int(estimated_monthly_clicks),
                'market_opportunity_monthly_eur': round(market_opportunity_monthly, 2),
                'market_opportunity_annual_eur': round(market_opportunity_annual, 2)
            },
            'competition_breakdown': competition_breakdown,
            'volume_segmentation': {
                'high_volume_count': len(high_volume),
                'medium_volume_count': len(medium_volume),
                'low_volume_count': len(low_volume)
            },
            'top_keywords': keyword_ideas[:20],
            'high_volume_low_competition': [
                kw for kw in keyword_ideas
                if kw['avg_monthly_searches'] >= 500 and kw['competition'] in ['LOW', 'MEDIUM']
            ][:10],
            'long_tail_opportunities': [
                kw for kw in keyword_ideas
                if kw['avg_monthly_searches'] < 500 and kw['avg_cpc_eur'] < weighted_cpc * 0.7
            ][:15]
        }

        logger.info(f"Market analysis complete: {total_monthly_searches:,} monthly searches")
        return analysis

    def competitor_keyword_research(
        self,
        competitor_domains: List[str],
        location_names: List[str] = None,
        language: str = 'french'
    ) -> Dict:
        """
        Analyze competitor keyword opportunities (URL-based)

        Args:
            competitor_domains: List of competitor URLs/domains
            location_names: Target locations
            language: Target language

        Returns:
            Competitor keyword analysis
        """
        logger.info(f"Analyzing competitor keywords: {competitor_domains}")

        # Default to France
        if not location_names:
            location_names = ['france']

        # Convert locations
        location_ids = [
            self.LOCATION_IDS.get(loc.lower(), '2250')
            for loc in location_names
        ]

        # Get language ID
        language_id = self.LANGUAGE_IDS.get(language.lower(), '1002')

        keyword_plan_idea_service = self.client.get_service("KeywordPlanIdeaService")

        all_competitor_keywords = []

        for domain in competitor_domains:
            try:
                request = self.client.get_type("GenerateKeywordIdeasRequest")
                request.customer_id = self.customer_id

                # Set location
                for location_id in location_ids:
                    request.geo_target_constants.append(f"geoTargetConstants/{location_id}")

                # Set language
                request.language = f"languageConstants/{language_id}"

                # URL seed
                request.url_seed.url = domain if domain.startswith('http') else f'https://{domain}'

                response = keyword_plan_idea_service.generate_keyword_ideas(request=request)

                competitor_keywords = []
                for idea in response.results:
                    metrics = idea.keyword_idea_metrics

                    competition = metrics.competition.name if hasattr(metrics, 'competition') else 'UNKNOWN'
                    low_cpc = metrics.low_top_of_page_bid_micros / 1_000_000 if metrics.low_top_of_page_bid_micros else 0
                    high_cpc = metrics.high_top_of_page_bid_micros / 1_000_000 if metrics.high_top_of_page_bid_micros else 0
                    avg_cpc = (low_cpc + high_cpc) / 2

                    competitor_keywords.append({
                        'keyword': idea.text,
                        'avg_monthly_searches': metrics.avg_monthly_searches,
                        'competition': competition,
                        'avg_cpc_eur': round(avg_cpc, 2),
                        'source_domain': domain
                    })

                # Sort by volume
                competitor_keywords.sort(key=lambda x: x['avg_monthly_searches'], reverse=True)
                all_competitor_keywords.extend(competitor_keywords[:50])  # Top 50 per competitor

                logger.info(f"Retrieved {len(competitor_keywords)} keywords from {domain}")

            except Exception as e:
                logger.error(f"Failed to analyze {domain}: {e}")
                continue

        # Remove duplicates (keep highest volume)
        unique_keywords = {}
        for kw in all_competitor_keywords:
            keyword_text = kw['keyword']
            if keyword_text not in unique_keywords or kw['avg_monthly_searches'] > unique_keywords[keyword_text]['avg_monthly_searches']:
                unique_keywords[keyword_text] = kw

        final_keywords = list(unique_keywords.values())
        final_keywords.sort(key=lambda x: x['avg_monthly_searches'], reverse=True)

        analysis = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'competitor_domains': competitor_domains,
                'locations': location_names,
                'language': language
            },
            'summary': {
                'total_keywords_found': len(final_keywords),
                'total_monthly_searches': sum(kw['avg_monthly_searches'] for kw in final_keywords)
            },
            'top_competitor_keywords': final_keywords[:30],
            'high_value_opportunities': [
                kw for kw in final_keywords
                if kw['avg_monthly_searches'] >= 500 and kw['competition'] != 'HIGH'
            ][:15]
        }

        logger.info(f"Competitor analysis complete: {len(final_keywords)} unique keywords")
        return analysis

    def export_analysis(self, analysis: Dict, output_path: str):
        """
        Export keyword analysis to JSON

        Args:
            analysis: Analysis dictionary
            output_path: Path to output file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            logger.info(f"Analysis exported to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export analysis: {e}")
            raise


# Main execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python keyword_planner_analyzer.py <credentials_path> <customer_id>")
        print("\nExample:")
        print("  python keyword_planner_analyzer.py google-ads.yaml 1234567890")
        sys.exit(1)

    credentials_path = sys.argv[1]
    customer_id = sys.argv[2]

    try:
        analyzer = KeywordPlannerAnalyzer(credentials_path, customer_id)

        # Example: Market volume analysis
        print("\n📊 Analyzing market volume...")

        seed_keywords = [
            "chaussures running",
            "basket sport",
            "running femme",
            "chaussures trail"
        ]

        market_analysis = analyzer.analyze_market_volume(
            primary_keywords=seed_keywords,
            location_names=['france'],
            language='french'
        )

        # Export analysis
        analyzer.export_analysis(market_analysis, "keyword_market_analysis.json")

        # Print summary
        print("\n" + "="*60)
        print("✅ ANALYSE MARCHÉ - KEYWORD PLANNER")
        print("="*60)

        summary = market_analysis['summary']
        print(f"\n📈 RÉSUMÉ:")
        print(f"   Mots-clés analysés: {summary['keywords_analyzed']}")
        print(f"   Recherches mensuelles totales: {summary['total_monthly_searches']:,}")
        print(f"   CPC moyen pondéré: €{summary['weighted_avg_cpc']}")
        print(f"   Opportunité mensuelle estimée: €{summary['market_opportunity_monthly_eur']:,.2f}")
        print(f"   Opportunité annuelle estimée: €{summary['market_opportunity_annual_eur']:,.2f}")

        print(f"\n🎯 TOP 5 MOTS-CLÉS:")
        for i, kw in enumerate(market_analysis['top_keywords'][:5], 1):
            print(f"   {i}. {kw['keyword']}")
            print(f"      Volume: {kw['avg_monthly_searches']:,} | CPC: €{kw['avg_cpc_eur']} | Competition: {kw['competition']}")

        print(f"\n💡 OPPORTUNITÉS (Volume élevé, faible concurrence): {len(market_analysis['high_volume_low_competition'])}")

        print(f"\n📁 Analyse complète exportée: keyword_market_analysis.json")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
