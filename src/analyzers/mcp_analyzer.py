"""
MCP Data Analysis Engine

MCP Server pour analyse données Google Ads
Prend les données extraites et produit des insights
"""

import json
import statistics
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Performance classification levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PerformanceMetrics:
    """Standard performance metrics"""
    roas: float
    ctr: float
    conversion_rate: float
    cpc: float
    quality_score: Optional[float] = None


class GoogleAdsAnalyzer:
    """Analyse données Google Ads avec benchmarks industrie"""

    # Benchmarks industrie (eCommerce) - Source: WordStream 2024
    INDUSTRY_BENCHMARKS = {
        'ctr': 0.04,  # 4%
        'conversion_rate': 0.025,  # 2.5%
        'avg_cpc': 1.50,  # €1.50
        'roas': 2.0,
        'quality_score': 7.5
    }

    def __init__(self, data_file: str):
        """
        Initialize analyzer with data file

        Args:
            data_file: Path to JSON file with extracted Google Ads data
        """
        logger.info(f"Loading data from {data_file}")
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            logger.info("Data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise

    def analyze_campaigns(self) -> Dict:
        """
        Analyse performance campagnes

        Returns:
            Dictionary with campaign analysis and recommendations
        """
        logger.info("Analyzing campaigns")
        campaigns = self.data.get('campaigns', [])

        if not campaigns:
            logger.warning("No campaign data found")
            return {'error': 'No campaign data available'}

        analysis = {
            'summary': {
                'total_campaigns': len(campaigns),
                'active_campaigns': len([c for c in campaigns if c['status'] == 'ENABLED']),
                'total_spend': 0,
                'total_conversions': 0,
                'total_revenue': 0,
                'overall_roas': 0,
                'avg_cpc': 0,
                'avg_ctr': 0,
                'avg_conversion_rate': 0
            },
            'by_performance': {
                'excellent': [],
                'good': [],
                'average': [],
                'poor': [],
                'critical': []
            },
            'by_channel': {},
            'by_bid_strategy': {},
            'recommendations': []
        }

        costs = []
        ctrs = []
        roas_values = []
        conv_rates = []

        for campaign in campaigns:
            cost = campaign.get('cost', 0)
            conversions = campaign.get('conversions', 0)
            revenue = campaign.get('conversion_value', 0)
            clicks = campaign.get('clicks', 0)
            impressions = campaign.get('impressions', 0)

            # Accumulate totals
            analysis['summary']['total_spend'] += cost
            analysis['summary']['total_conversions'] += conversions
            analysis['summary']['total_revenue'] += revenue

            # Collect metrics for averages
            if cost > 0:
                costs.append(campaign.get('avg_cpc', 0))
                roas_values.append(campaign.get('roas', 0))

            if impressions > 0:
                ctrs.append(campaign.get('ctr', 0))

            if clicks > 0 and conversions > 0:
                conv_rate = conversions / clicks
                conv_rates.append(conv_rate)

            # Classify campaign performance
            perf_level = self._classify_performance(campaign)
            analysis['by_performance'][perf_level.value].append({
                'id': campaign.get('id'),
                'name': campaign.get('name'),
                'roas': campaign.get('roas', 0),
                'ctr': campaign.get('ctr', 0),
                'cost': cost,
                'conversions': conversions,
                'revenue': revenue,
                'status': campaign.get('status')
            })

            # Group by channel
            channel = campaign.get('channel_type', 'UNKNOWN')
            if channel not in analysis['by_channel']:
                analysis['by_channel'][channel] = {
                    'count': 0,
                    'total_spend': 0,
                    'total_revenue': 0,
                    'avg_roas': 0
                }
            analysis['by_channel'][channel]['count'] += 1
            analysis['by_channel'][channel]['total_spend'] += cost
            analysis['by_channel'][channel]['total_revenue'] += revenue

            # Group by bid strategy
            bid_strategy = campaign.get('bid_strategy', 'UNKNOWN')
            if bid_strategy not in analysis['by_bid_strategy']:
                analysis['by_bid_strategy'][bid_strategy] = {
                    'count': 0,
                    'total_spend': 0,
                    'total_revenue': 0,
                    'avg_roas': 0
                }
            analysis['by_bid_strategy'][bid_strategy]['count'] += 1
            analysis['by_bid_strategy'][bid_strategy]['total_spend'] += cost
            analysis['by_bid_strategy'][bid_strategy]['total_revenue'] += revenue

        # Calculate averages
        analysis['summary']['avg_cpc'] = statistics.mean(costs) if costs else 0
        analysis['summary']['avg_ctr'] = statistics.mean(ctrs) if ctrs else 0
        analysis['summary']['avg_conversion_rate'] = statistics.mean(conv_rates) if conv_rates else 0

        total_spend = analysis['summary']['total_spend']
        total_revenue = analysis['summary']['total_revenue']
        analysis['summary']['overall_roas'] = total_revenue / total_spend if total_spend > 0 else 0

        # Calculate channel ROAS
        for channel in analysis['by_channel']:
            ch_data = analysis['by_channel'][channel]
            if ch_data['total_spend'] > 0:
                ch_data['avg_roas'] = ch_data['total_revenue'] / ch_data['total_spend']

        # Calculate bid strategy ROAS
        for strategy in analysis['by_bid_strategy']:
            bs_data = analysis['by_bid_strategy'][strategy]
            if bs_data['total_spend'] > 0:
                bs_data['avg_roas'] = bs_data['total_revenue'] / bs_data['total_spend']

        # Generate recommendations
        analysis['recommendations'] = self._generate_campaign_recommendations(analysis)

        logger.info("Campaign analysis complete")
        return analysis

    def analyze_keywords(self) -> Dict:
        """
        Analyse efficacité mots-clés

        Returns:
            Dictionary with keyword analysis and recommendations
        """
        logger.info("Analyzing keywords")
        keywords = self.data.get('keywords', [])

        if not keywords:
            logger.warning("No keyword data found")
            return {'error': 'No keyword data available'}

        analysis = {
            'summary': {
                'total_keywords': len(keywords),
                'avg_quality_score': 0,
                'keywords_with_qs_below_5': 0,
                'keywords_with_qs_above_8': 0,
                'total_spend': 0,
                'total_conversions': 0
            },
            'low_quality_score': [],
            'high_cpc_low_conv': [],
            'high_volume_low_ctr': [],
            'winner_keywords': [],
            'negative_keyword_candidates': [],
            'by_match_type': {},
            'recommendations': []
        }

        quality_scores = []
        total_spend = 0
        total_conversions = 0

        for kw in keywords:
            cost = kw.get('cost', 0)
            conversions = kw.get('conversions', 0)
            impressions = kw.get('impressions', 0)
            ctr = kw.get('ctr', 0)
            avg_cpc = kw.get('avg_cpc', 0)
            conv_value = kw.get('conversion_value', 0)

            total_spend += cost
            total_conversions += conversions

            # Quality score analysis
            qs = kw.get('quality_score')
            if qs is not None:
                quality_scores.append(qs)
                if qs < 5:
                    analysis['summary']['keywords_with_qs_below_5'] += 1
                    analysis['low_quality_score'].append(kw)
                elif qs >= 8:
                    analysis['summary']['keywords_with_qs_above_8'] += 1

            # High CPC but low conversions
            if avg_cpc > self.INDUSTRY_BENCHMARKS['avg_cpc'] * 1.5 and conversions == 0 and cost > 10:
                analysis['high_cpc_low_conv'].append(kw)

            # High impressions but low CTR
            if impressions > 100 and ctr < self.INDUSTRY_BENCHMARKS['ctr']:
                analysis['high_volume_low_ctr'].append(kw)

            # Winner keywords (high ROAS, consistent conversions)
            if conversions > 5:
                roas = conv_value / cost if cost > 0 else 0
                if roas > self.INDUSTRY_BENCHMARKS['roas']:
                    analysis['winner_keywords'].append({
                        **kw,
                        'roas': roas
                    })

            # Negative keyword candidates (high spend, zero conversions)
            if cost > 50 and conversions == 0:
                analysis['negative_keyword_candidates'].append(kw)

            # Group by match type
            match_type = kw.get('match_type', 'UNKNOWN')
            if match_type not in analysis['by_match_type']:
                analysis['by_match_type'][match_type] = {
                    'count': 0,
                    'total_spend': 0,
                    'total_conversions': 0,
                    'avg_cpc': 0
                }
            analysis['by_match_type'][match_type]['count'] += 1
            analysis['by_match_type'][match_type]['total_spend'] += cost
            analysis['by_match_type'][match_type]['total_conversions'] += conversions

        # Calculate averages
        analysis['summary']['avg_quality_score'] = statistics.mean(quality_scores) if quality_scores else 0
        analysis['summary']['total_spend'] = total_spend
        analysis['summary']['total_conversions'] = total_conversions

        # Calculate match type avg CPC
        for match_type in analysis['by_match_type']:
            mt_data = analysis['by_match_type'][match_type]
            if mt_data['count'] > 0:
                # Average CPC would need individual keyword CPCs
                pass

        # Sort lists by cost (descending)
        analysis['low_quality_score'].sort(key=lambda x: x.get('cost', 0), reverse=True)
        analysis['high_cpc_low_conv'].sort(key=lambda x: x.get('cost', 0), reverse=True)
        analysis['winner_keywords'].sort(key=lambda x: x.get('roas', 0), reverse=True)
        analysis['negative_keyword_candidates'].sort(key=lambda x: x.get('cost', 0), reverse=True)

        # Limit to top items
        analysis['low_quality_score'] = analysis['low_quality_score'][:20]
        analysis['high_cpc_low_conv'] = analysis['high_cpc_low_conv'][:20]
        analysis['winner_keywords'] = analysis['winner_keywords'][:20]
        analysis['negative_keyword_candidates'] = analysis['negative_keyword_candidates'][:20]

        # Generate recommendations
        analysis['recommendations'] = self._generate_keyword_recommendations(analysis)

        logger.info("Keyword analysis complete")
        return analysis

    def analyze_shopping_feed(self) -> Dict:
        """
        Analyse qualité feed Merchant Center

        Returns:
            Dictionary with shopping feed analysis
        """
        logger.info("Analyzing Shopping feed")
        products = self.data.get('products', [])

        if not products:
            logger.warning("No Shopping data found")
            return {'error': 'No Shopping data available'}

        analysis = {
            'summary': {
                'total_products_tracked': len(products),
                'total_spend': 0,
                'total_revenue': 0,
                'overall_roas': 0
            },
            'by_category_l1': {},
            'by_category_l2': {},
            'low_roas_products': [],
            'high_roas_products': [],
            'high_spend_low_conv': [],
            'recommendations': []
        }

        total_spend = 0
        total_revenue = 0

        for product in products:
            cost = product.get('cost', 0)
            conv_value = product.get('conversion_value', 0)
            conversions = product.get('conversions', 0)
            roas = product.get('roas', 0)

            total_spend += cost
            total_revenue += conv_value

            # Group by category L1
            category_l1 = product.get('product_category_l1', 'Uncategorized')
            if category_l1 not in analysis['by_category_l1']:
                analysis['by_category_l1'][category_l1] = {
                    'count': 0,
                    'total_spend': 0,
                    'total_revenue': 0,
                    'total_conversions': 0,
                    'avg_roas': 0
                }

            analysis['by_category_l1'][category_l1]['count'] += 1
            analysis['by_category_l1'][category_l1]['total_spend'] += cost
            analysis['by_category_l1'][category_l1]['total_revenue'] += conv_value
            analysis['by_category_l1'][category_l1]['total_conversions'] += conversions

            # Group by category L2
            category_l2 = product.get('product_category_l2', 'Uncategorized')
            if category_l2 not in analysis['by_category_l2']:
                analysis['by_category_l2'][category_l2] = {
                    'count': 0,
                    'total_spend': 0,
                    'total_revenue': 0,
                    'total_conversions': 0,
                    'avg_roas': 0
                }

            analysis['by_category_l2'][category_l2]['count'] += 1
            analysis['by_category_l2'][category_l2]['total_spend'] += cost
            analysis['by_category_l2'][category_l2]['total_revenue'] += conv_value
            analysis['by_category_l2'][category_l2]['total_conversions'] += conversions

            # Identify problem products
            if roas < 0.5 and cost > 10:
                analysis['low_roas_products'].append(product)

            # Identify high performers
            if roas > 3.0 and conversions > 2:
                analysis['high_roas_products'].append(product)

            # High spend, low conversion
            if cost > 50 and conversions == 0:
                analysis['high_spend_low_conv'].append(product)

        # Calculate category ROAS
        for category in analysis['by_category_l1']:
            cat_data = analysis['by_category_l1'][category]
            if cat_data['total_spend'] > 0:
                cat_data['avg_roas'] = cat_data['total_revenue'] / cat_data['total_spend']

        for category in analysis['by_category_l2']:
            cat_data = analysis['by_category_l2'][category]
            if cat_data['total_spend'] > 0:
                cat_data['avg_roas'] = cat_data['total_revenue'] / cat_data['total_spend']

        # Summary
        analysis['summary']['total_spend'] = total_spend
        analysis['summary']['total_revenue'] = total_revenue
        analysis['summary']['overall_roas'] = total_revenue / total_spend if total_spend > 0 else 0

        # Sort products by ROAS
        analysis['low_roas_products'].sort(key=lambda x: x.get('cost', 0), reverse=True)
        analysis['high_roas_products'].sort(key=lambda x: x.get('roas', 0), reverse=True)
        analysis['high_spend_low_conv'].sort(key=lambda x: x.get('cost', 0), reverse=True)

        # Limit to top 20
        analysis['low_roas_products'] = analysis['low_roas_products'][:20]
        analysis['high_roas_products'] = analysis['high_roas_products'][:20]
        analysis['high_spend_low_conv'] = analysis['high_spend_low_conv'][:20]

        # Generate recommendations
        analysis['recommendations'] = self._generate_feed_recommendations(analysis)

        logger.info("Shopping feed analysis complete")
        return analysis

    def analyze_search_terms(self) -> Dict:
        """
        Analyze search terms to identify negative keyword opportunities

        Returns:
            Dictionary with search term analysis
        """
        logger.info("Analyzing search terms")
        search_terms = self.data.get('search_terms', [])

        if not search_terms:
            logger.warning("No search term data found")
            return {'error': 'No search term data available'}

        analysis = {
            'summary': {
                'total_search_terms': len(search_terms),
                'total_spend': 0,
                'total_conversions': 0
            },
            'negative_keyword_candidates': [],
            'high_volume_winners': [],
            'by_match_type': {},
            'recommendations': []
        }

        total_spend = 0
        total_conversions = 0

        for term in search_terms:
            cost = term.get('cost', 0)
            conversions = term.get('conversions', 0)
            impressions = term.get('impressions', 0)
            match_type = term.get('match_type', 'UNKNOWN')

            total_spend += cost
            total_conversions += conversions

            # Negative keyword candidates
            if cost > 20 and conversions == 0:
                analysis['negative_keyword_candidates'].append(term)

            # High volume winners
            if conversions > 3 and impressions > 100:
                roas = term.get('conversion_value', 0) / cost if cost > 0 else 0
                if roas > self.INDUSTRY_BENCHMARKS['roas']:
                    analysis['high_volume_winners'].append({
                        **term,
                        'roas': roas
                    })

            # Group by match type
            if match_type not in analysis['by_match_type']:
                analysis['by_match_type'][match_type] = {
                    'count': 0,
                    'total_spend': 0,
                    'total_conversions': 0
                }
            analysis['by_match_type'][match_type]['count'] += 1
            analysis['by_match_type'][match_type]['total_spend'] += cost
            analysis['by_match_type'][match_type]['total_conversions'] += conversions

        analysis['summary']['total_spend'] = total_spend
        analysis['summary']['total_conversions'] = total_conversions

        # Sort and limit
        analysis['negative_keyword_candidates'].sort(key=lambda x: x.get('cost', 0), reverse=True)
        analysis['high_volume_winners'].sort(key=lambda x: x.get('roas', 0), reverse=True)

        analysis['negative_keyword_candidates'] = analysis['negative_keyword_candidates'][:30]
        analysis['high_volume_winners'] = analysis['high_volume_winners'][:20]

        logger.info("Search term analysis complete")
        return analysis

    def forecast_roas(self, current_roas: float, interventions: List[str]) -> Dict:
        """
        Prévision ROAS après implémentation recommandations

        Args:
            current_roas: Current ROAS value
            interventions: List of optimization interventions to apply

        Returns:
            Dictionary with forecast results
        """
        logger.info(f"Forecasting ROAS with interventions: {interventions}")

        improvements = {
            'quality_score_optimization': 0.15,  # +15% ROAS
            'feed_enhancement': 0.10,  # +10% ROAS
            'keyword_cleanup': 0.12,  # +12% ROAS
            'bid_strategy_optimization': 0.20,  # +20% ROAS
            'negative_keywords': 0.08,  # +8% ROAS
            'seasonal_budgeting': 0.18,  # +18% ROAS
            'campaign_restructure': 0.25,  # +25% ROAS
            'shopping_feed_optimization': 0.15,  # +15% ROAS
            'landing_page_optimization': 0.20,  # +20% ROAS
            'audience_targeting': 0.12,  # +12% ROAS
        }

        total_improvement = 1.0
        implemented = []

        for intervention in interventions:
            if intervention in improvements:
                total_improvement *= (1 + improvements[intervention])
                implemented.append({
                    'name': intervention,
                    'expected_lift': improvements[intervention]
                })

        forecasted_roas = current_roas * total_improvement
        improvement_pct = (forecasted_roas / current_roas - 1) * 100 if current_roas > 0 else 0

        # Determine confidence level
        if len(implemented) >= 4:
            confidence = 'high'
        elif len(implemented) >= 2:
            confidence = 'medium'
        else:
            confidence = 'low'

        result = {
            'current_roas': round(current_roas, 2),
            'forecasted_roas': round(forecasted_roas, 2),
            'improvement_pct': round(improvement_pct, 1),
            'interventions_implemented': implemented,
            'confidence': confidence,
            'total_improvement_factor': round(total_improvement, 3)
        }

        logger.info(f"ROAS forecast: {current_roas:.2f} → {forecasted_roas:.2f} (+{improvement_pct:.1f}%)")
        return result

    def generate_full_report(self, output_path: str = "mcp_analysis_output.json"):
        """
        Generate complete analysis report

        Args:
            output_path: Path to output JSON file
        """
        logger.info("Generating full analysis report")

        campaign_analysis = self.analyze_campaigns()
        keyword_analysis = self.analyze_keywords()
        shopping_analysis = self.analyze_shopping_feed()
        search_term_analysis = self.analyze_search_terms()

        # Determine recommended interventions based on findings
        recommended_interventions = []
        current_roas = campaign_analysis.get('summary', {}).get('overall_roas', 0)

        if len(keyword_analysis.get('low_quality_score', [])) > 5:
            recommended_interventions.append('quality_score_optimization')

        if len(keyword_analysis.get('negative_keyword_candidates', [])) > 10:
            recommended_interventions.append('negative_keywords')

        if current_roas < 1.5:
            recommended_interventions.append('bid_strategy_optimization')
            recommended_interventions.append('campaign_restructure')

        if len(shopping_analysis.get('low_roas_products', [])) > 10:
            recommended_interventions.append('shopping_feed_optimization')

        # Generate forecast
        forecast = self.forecast_roas(current_roas, recommended_interventions)

        # Compile full report
        report = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'data_source': self.data.get('metadata', {}),
                'analyzer_version': '1.0.0'
            },
            'executive_summary': {
                'current_roas': current_roas,
                'forecasted_roas': forecast['forecasted_roas'],
                'improvement_potential': forecast['improvement_pct'],
                'total_spend': campaign_analysis.get('summary', {}).get('total_spend', 0),
                'total_revenue': campaign_analysis.get('summary', {}).get('total_revenue', 0),
                'critical_issues_count': len(campaign_analysis.get('by_performance', {}).get('critical', []))
            },
            'campaigns': campaign_analysis,
            'keywords': keyword_analysis,
            'shopping': shopping_analysis,
            'search_terms': search_term_analysis,
            'forecast': forecast,
            'priority_recommendations': self._generate_priority_recommendations(
                campaign_analysis, keyword_analysis, shopping_analysis
            )
        }

        # Export report
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Full report exported to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            raise

        return report

    def _classify_performance(self, campaign: Dict) -> PerformanceLevel:
        """Classe la performance d'une campagne"""
        roas = campaign.get('roas', 0)

        if roas >= 4.0:
            return PerformanceLevel.EXCELLENT
        elif roas >= 2.5:
            return PerformanceLevel.GOOD
        elif roas >= 1.5:
            return PerformanceLevel.AVERAGE
        elif roas >= 0.8:
            return PerformanceLevel.POOR
        else:
            return PerformanceLevel.CRITICAL

    def _generate_campaign_recommendations(self, analysis: Dict) -> List[str]:
        """Recommandations niveau campagnes"""
        recommendations = []

        summary = analysis.get('summary', {})
        by_performance = analysis.get('by_performance', {})

        # Analyze critical campaigns
        critical_count = len(by_performance.get('critical', []))
        if critical_count > 0:
            recommendations.append(
                f"🚨 CRITIQUE: {critical_count} campagne(s) avec ROAS < 0.8. "
                f"Action immédiate: vérifier le tracking de conversions et l'audience ciblée."
            )

        # Overall ROAS check
        overall_roas = summary.get('overall_roas', 0)
        if overall_roas < 1.5:
            recommendations.append(
                f"⚠️ ROAS global à {overall_roas:.2f}. "
                f"Recommandation: réviser la stratégie d'enchères et restructurer les campagnes."
            )
        elif overall_roas > 3.0:
            recommendations.append(
                f"✅ Excellent ROAS global ({overall_roas:.2f}). "
                f"Opportunité: augmenter le budget pour scaler les campagnes performantes."
            )

        # CTR analysis
        avg_ctr = summary.get('avg_ctr', 0)
        benchmark_ctr = self.INDUSTRY_BENCHMARKS['ctr']
        if avg_ctr < benchmark_ctr:
            recommendations.append(
                f"📝 CTR moyen {avg_ctr:.2%} < benchmark industrie {benchmark_ctr:.2%}. "
                f"Action: améliorer les copies d'annonces, images et extensions."
            )

        # Check for excellent performers
        excellent_count = len(by_performance.get('excellent', []))
        if excellent_count > 0:
            recommendations.append(
                f"🏆 {excellent_count} campagne(s) excellente(s) (ROAS ≥ 4.0). "
                f"Action: dupliquer la structure et augmenter le budget."
            )

        return recommendations

    def _generate_keyword_recommendations(self, analysis: Dict) -> List[str]:
        """Recommandations niveau mots-clés"""
        recommendations = []

        # Low quality score
        low_qs_count = len(analysis.get('low_quality_score', []))
        if low_qs_count > 0:
            recommendations.append(
                f"📊 {low_qs_count} mot(s)-clé(s) avec Quality Score < 5. "
                f"Impact: CPC augmenté de 30-50%. Améliorer landing pages, ad copy et CTR."
            )

        # High CPC low conversion
        high_cpc_count = len(analysis.get('high_cpc_low_conv', []))
        if high_cpc_count > 0:
            recommendations.append(
                f"💰 {high_cpc_count} mot(s)-clé(s) coûteux sans conversion. "
                f"Action: ajouter à la liste de mots-clés négatifs ou ajuster les enchères."
            )

        # Winner keywords
        winner_count = len(analysis.get('winner_keywords', []))
        if winner_count > 0:
            recommendations.append(
                f"✅ {winner_count} mot(s)-clé(s) gagnant(s) identifié(s). "
                f"Action: augmenter les enchères et créer des campagnes dédiées SKAG."
            )

        # Negative keyword candidates
        neg_kw_count = len(analysis.get('negative_keyword_candidates', []))
        if neg_kw_count > 0:
            total_waste = sum(kw.get('cost', 0) for kw in analysis.get('negative_keyword_candidates', []))
            recommendations.append(
                f"🚫 {neg_kw_count} mot(s)-clé(s) à ajouter en négatif (€{total_waste:.2f} de dépenses inutiles). "
                f"Action: créer une liste de mots-clés négatifs partagée."
            )

        return recommendations

    def _generate_feed_recommendations(self, analysis: Dict) -> List[str]:
        """Recommandations Merchant Center"""
        recommendations = []

        # Low ROAS products
        low_roas_count = len(analysis.get('low_roas_products', []))
        if low_roas_count > 0:
            recommendations.append(
                f"📦 {low_roas_count} produit(s) avec faible ROAS (< 0.5). "
                f"Vérifier: prix compétitif, qualité des images, descriptions, et ciblage."
            )

        # High ROAS products
        high_roas_count = len(analysis.get('high_roas_products', []))
        if high_roas_count > 0:
            recommendations.append(
                f"🏆 {high_roas_count} produit(s) très performant(s) (ROAS > 3.0). "
                f"Action: augmenter les enchères et le budget sur ces produits."
            )

        # Best category
        categories = analysis.get('by_category_l1', {})
        if categories:
            best_category = max(
                categories.items(),
                key=lambda x: x[1].get('avg_roas', 0)
            )
            if best_category[1].get('avg_roas', 0) > 0:
                recommendations.append(
                    f"🎯 Catégorie '{best_category[0]}' performe le mieux (ROAS: {best_category[1]['avg_roas']:.2f}). "
                    f"Allouer plus de budget prioritairement à cette catégorie."
                )

        # High spend no conversion
        high_spend_count = len(analysis.get('high_spend_low_conv', []))
        if high_spend_count > 0:
            waste = sum(p.get('cost', 0) for p in analysis.get('high_spend_low_conv', []))
            recommendations.append(
                f"⚠️ {high_spend_count} produit(s) avec dépenses élevées mais zéro conversion (€{waste:.2f}). "
                f"Action: exclure ces produits ou vérifier leur page produit."
            )

        return recommendations

    def _generate_priority_recommendations(
        self, campaign_analysis: Dict, keyword_analysis: Dict, shopping_analysis: Dict
    ) -> List[Dict]:
        """Generate prioritized action items"""

        recommendations = []

        # Priority 1: Critical campaigns
        critical_campaigns = campaign_analysis.get('by_performance', {}).get('critical', [])
        if critical_campaigns:
            recommendations.append({
                'priority': 1,
                'category': 'Campaign Performance',
                'action': f'Fix {len(critical_campaigns)} critical campaign(s) with ROAS < 0.8',
                'expected_impact': 'High',
                'effort': 'Medium',
                'timeline': 'Week 1'
            })

        # Priority 2: Negative keywords
        neg_kw_candidates = keyword_analysis.get('negative_keyword_candidates', [])
        if len(neg_kw_candidates) > 10:
            waste = sum(kw.get('cost', 0) for kw in neg_kw_candidates)
            recommendations.append({
                'priority': 1,
                'category': 'Keyword Optimization',
                'action': f'Add {len(neg_kw_candidates)} negative keywords to stop waste (€{waste:.2f})',
                'expected_impact': 'High',
                'effort': 'Low',
                'timeline': 'Week 1'
            })

        # Priority 3: Low quality score
        low_qs = keyword_analysis.get('low_quality_score', [])
        if len(low_qs) > 5:
            recommendations.append({
                'priority': 2,
                'category': 'Quality Score',
                'action': f'Improve {len(low_qs)} keywords with QS < 5',
                'expected_impact': 'Medium',
                'effort': 'High',
                'timeline': 'Week 2-4'
            })

        # Priority 4: Shopping feed optimization
        low_roas_products = shopping_analysis.get('low_roas_products', [])
        if len(low_roas_products) > 10:
            recommendations.append({
                'priority': 2,
                'category': 'Shopping Feed',
                'action': f'Optimize or exclude {len(low_roas_products)} low-performing products',
                'expected_impact': 'Medium',
                'effort': 'Medium',
                'timeline': 'Week 2-3'
            })

        # Priority 5: Scale winners
        winner_keywords = keyword_analysis.get('winner_keywords', [])
        if len(winner_keywords) > 3:
            recommendations.append({
                'priority': 3,
                'category': 'Scaling',
                'action': f'Scale {len(winner_keywords)} high-ROAS keywords with increased budget',
                'expected_impact': 'High',
                'effort': 'Low',
                'timeline': 'Week 3-4'
            })

        return recommendations


# Main Execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python mcp_analyzer.py <data_file>")
        print("Example: python mcp_analyzer.py google_ads_data.json")
        sys.exit(1)

    data_file = sys.argv[1]

    try:
        analyzer = GoogleAdsAnalyzer(data_file)

        # Generate full report
        report = analyzer.generate_full_report("mcp_analysis_output.json")

        # Print summary
        print("\n" + "="*60)
        print("✅ ANALYSE COMPLÈTE - GOOGLE ADS")
        print("="*60)

        exec_summary = report['executive_summary']
        print(f"\n📊 RÉSUMÉ EXÉCUTIF:")
        print(f"   ROAS Actuel: {exec_summary['current_roas']:.2f}")
        print(f"   ROAS Prévisionnel: {exec_summary['forecasted_roas']:.2f}")
        print(f"   Amélioration Potentielle: +{exec_summary['improvement_potential']:.1f}%")
        print(f"   Dépenses Totales: €{exec_summary['total_spend']:,.2f}")
        print(f"   Revenus Totaux: €{exec_summary['total_revenue']:,.2f}")

        print(f"\n🎯 RECOMMANDATIONS PRIORITAIRES:")
        for i, rec in enumerate(report['priority_recommendations'][:5], 1):
            print(f"\n   {i}. [{rec['priority']}] {rec['category']}")
            print(f"      Action: {rec['action']}")
            print(f"      Impact: {rec['expected_impact']} | Effort: {rec['effort']} | Timeline: {rec['timeline']}")

        print(f"\n📁 Rapport complet exporté: mcp_analysis_output.json")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
