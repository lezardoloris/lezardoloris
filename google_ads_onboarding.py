#!/usr/bin/env python3
"""
Google Ads Expert Onboarding System - Main CLI

Système complet d'onboarding pour consultants Google Ads freelance et agences
"""

import click
import json
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
import logging

# Import custom modules
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from extractors.google_ads_extractor import GoogleAdsExtractor
from analyzers.mcp_analyzer import GoogleAdsAnalyzer
from analyzers.keyword_planner_analyzer import KeywordPlannerAnalyzer

# Setup console for rich output
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_ads_onboarding.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    🚀 Google Ads Expert Onboarding System

    Système complet pour auditer, analyser et optimiser les comptes Google Ads
    """
    pass


@cli.command()
@click.option('--credentials', '-c', required=True, help='Path to Google Ads API credentials (YAML)')
@click.option('--customer-id', '-i', required=True, help='Google Ads Customer ID (without hyphens)')
@click.option('--days', '-d', default=30, help='Number of days to extract (default: 30)')
@click.option('--output', '-o', default='google_ads_data.json', help='Output file path')
def extract(credentials, customer_id, days, output):
    """Extract data from Google Ads account"""

    console.print(Panel.fit(
        "📊 [bold cyan]Google Ads Data Extraction[/bold cyan]",
        border_style="cyan"
    ))

    try:
        console.print(f"\n[yellow]Initializing extractor for customer {customer_id}...[/yellow]")
        extractor = GoogleAdsExtractor(credentials, customer_id)

        console.print(f"[yellow]Extracting {days} days of data...[/yellow]\n")

        # Extract all data with progress indication
        with console.status("[bold green]Extracting campaigns...") as status:
            campaigns = extractor.extract_campaign_data(days)
            console.print(f"✅ Extracted {len(campaigns)} campaigns")

            status.update("[bold green]Extracting keywords...")
            keywords = extractor.extract_keyword_data()
            console.print(f"✅ Extracted {len(keywords)} keywords")

            status.update("[bold green]Extracting shopping products...")
            products = extractor.extract_shopping_data()
            console.print(f"✅ Extracted {len(products)} products")

            status.update("[bold green]Extracting search terms...")
            search_terms = extractor.extract_search_terms()
            console.print(f"✅ Extracted {len(search_terms)} search terms")

        # Compile data
        data = {
            'metadata': {
                'customer_id': customer_id,
                'extraction_date': datetime.now().isoformat(),
                'date_range_days': days,
            },
            'campaigns': campaigns,
            'keywords': keywords,
            'products': products,
            'search_terms': search_terms
        }

        # Export
        extractor.export_to_json(data, output)

        console.print(f"\n[bold green]✅ Data extraction complete![/bold green]")
        console.print(f"📁 Data saved to: [cyan]{output}[/cyan]\n")

        # Show summary table
        table = Table(title="Extraction Summary")
        table.add_column("Data Type", style="cyan")
        table.add_column("Count", justify="right", style="green")

        table.add_row("Campaigns", str(len(campaigns)))
        table.add_row("Keywords", str(len(keywords)))
        table.add_row("Products", str(len(products)))
        table.add_row("Search Terms", str(len(search_terms)))

        console.print(table)

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        logger.error(f"Extraction failed: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.option('--data-file', '-d', required=True, help='Path to extracted Google Ads data JSON')
@click.option('--output', '-o', default='analysis_report.json', help='Output analysis file')
def analyze(data_file, output):
    """Analyze extracted Google Ads data"""

    console.print(Panel.fit(
        "🔍 [bold magenta]Google Ads Data Analysis[/bold magenta]",
        border_style="magenta"
    ))

    try:
        console.print(f"\n[yellow]Loading data from {data_file}...[/yellow]")
        analyzer = GoogleAdsAnalyzer(data_file)

        console.print("[yellow]Running comprehensive analysis...[/yellow]\n")

        with console.status("[bold green]Analyzing campaigns...") as status:
            campaign_analysis = analyzer.analyze_campaigns()
            console.print("✅ Campaign analysis complete")

            status.update("[bold green]Analyzing keywords...")
            keyword_analysis = analyzer.analyze_keywords()
            console.print("✅ Keyword analysis complete")

            status.update("[bold green]Analyzing shopping feed...")
            shopping_analysis = analyzer.analyze_shopping_feed()
            console.print("✅ Shopping analysis complete")

            status.update("[bold green]Analyzing search terms...")
            search_term_analysis = analyzer.analyze_search_terms()
            console.print("✅ Search term analysis complete")

            status.update("[bold green]Generating forecast...")

            # Generate forecast
            current_roas = campaign_analysis.get('summary', {}).get('overall_roas', 0)
            interventions = ['quality_score_optimization', 'keyword_cleanup', 'bid_strategy_optimization']
            forecast = analyzer.forecast_roas(current_roas, interventions)
            console.print("✅ Forecast generated")

        # Compile report
        report = analyzer.generate_full_report(output)

        console.print(f"\n[bold green]✅ Analysis complete![/bold green]")
        console.print(f"📁 Report saved to: [cyan]{output}[/cyan]\n")

        # Display executive summary
        exec_summary = report['executive_summary']

        summary_table = Table(title="Executive Summary", border_style="blue")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", justify="right", style="green")

        summary_table.add_row("Current ROAS", f"{exec_summary['current_roas']:.2f}")
        summary_table.add_row("Forecasted ROAS", f"[bold]{exec_summary['forecasted_roas']:.2f}[/bold]")
        summary_table.add_row("Improvement Potential", f"+{exec_summary['improvement_potential']:.1f}%")
        summary_table.add_row("Total Spend", f"€{exec_summary['total_spend']:,.2f}")
        summary_table.add_row("Total Revenue", f"€{exec_summary['total_revenue']:,.2f}")
        summary_table.add_row("Critical Issues", str(exec_summary['critical_issues_count']))

        console.print(summary_table)

        # Display top recommendations
        console.print("\n[bold cyan]🎯 Priority Recommendations:[/bold cyan]\n")
        for i, rec in enumerate(report['priority_recommendations'][:5], 1):
            priority_emoji = "🔴" if rec['priority'] == 1 else "🟠" if rec['priority'] == 2 else "🟡"
            console.print(f"{priority_emoji} [bold]{rec['category']}[/bold]")
            console.print(f"   {rec['action']}")
            console.print(f"   Impact: {rec['expected_impact']} | Effort: {rec['effort']} | Timeline: {rec['timeline']}\n")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        logger.error(f"Analysis failed: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.option('--credentials', '-c', required=True, help='Path to Google Ads API credentials')
@click.option('--customer-id', '-i', required=True, help='Google Ads Customer ID')
@click.option('--keywords', '-k', required=True, help='Comma-separated seed keywords')
@click.option('--locations', '-l', default='france', help='Comma-separated locations (default: france)')
@click.option('--language', default='french', help='Language (default: french)')
@click.option('--output', '-o', default='keyword_analysis.json', help='Output file')
def keyword_research(credentials, customer_id, keywords, locations, language, output):
    """Research keywords using Google Keyword Planner"""

    console.print(Panel.fit(
        "🔎 [bold yellow]Keyword Research & Market Analysis[/bold yellow]",
        border_style="yellow"
    ))

    try:
        console.print(f"\n[yellow]Initializing Keyword Planner...[/yellow]")
        analyzer = KeywordPlannerAnalyzer(credentials, customer_id)

        seed_keywords = [kw.strip() for kw in keywords.split(',')]
        location_list = [loc.strip() for loc in locations.split(',')]

        console.print(f"\n[yellow]Seed Keywords:[/yellow] {', '.join(seed_keywords)}")
        console.print(f"[yellow]Locations:[/yellow] {', '.join(location_list)}")
        console.print(f"[yellow]Language:[/yellow] {language}\n")

        with console.status("[bold green]Analyzing market volume..."):
            market_analysis = analyzer.analyze_market_volume(
                primary_keywords=seed_keywords,
                location_names=location_list,
                language=language
            )

        # Export
        analyzer.export_analysis(market_analysis, output)

        console.print(f"\n[bold green]✅ Keyword research complete![/bold green]")
        console.print(f"📁 Analysis saved to: [cyan]{output}[/cyan]\n")

        # Display summary
        summary = market_analysis['summary']

        kw_table = Table(title="Market Analysis", border_style="yellow")
        kw_table.add_column("Metric", style="cyan")
        kw_table.add_column("Value", justify="right", style="green")

        kw_table.add_row("Keywords Analyzed", str(summary['keywords_analyzed']))
        kw_table.add_row("Total Monthly Searches", f"{summary['total_monthly_searches']:,}")
        kw_table.add_row("Weighted Avg CPC", f"€{summary['weighted_avg_cpc']}")
        kw_table.add_row("Market Opportunity (Monthly)", f"€{summary['market_opportunity_monthly_eur']:,.2f}")
        kw_table.add_row("Market Opportunity (Annual)", f"€{summary['market_opportunity_annual_eur']:,.2f}")

        console.print(kw_table)

        # Top keywords
        console.print("\n[bold cyan]🏆 Top 5 Keywords:[/bold cyan]\n")
        for i, kw in enumerate(market_analysis['top_keywords'][:5], 1):
            console.print(f"{i}. [bold]{kw['keyword']}[/bold]")
            console.print(f"   Volume: {kw['avg_monthly_searches']:,} | CPC: €{kw['avg_cpc_eur']} | Competition: {kw['competition']}\n")

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
        logger.error(f"Keyword research failed: {e}", exc_info=True)
        sys.exit(1)


@cli.command()
@click.option('--credentials', '-c', required=True, help='Path to Google Ads API credentials')
@click.option('--customer-id', '-i', required=True, help='Google Ads Customer ID')
@click.option('--days', '-d', default=30, help='Days to extract')
@click.option('--client-name', required=True, help='Client name for reports')
def full_audit(credentials, customer_id, days, client_name):
    """Run complete audit: extract + analyze + keyword research"""

    console.print(Panel.fit(
        f"🚀 [bold green]Full Google Ads Audit - {client_name}[/bold green]",
        border_style="green"
    ))

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(f'audits/{client_name}_{timestamp}')
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n📁 Output directory: [cyan]{output_dir}[/cyan]\n")

    # Step 1: Extract
    console.print("[bold cyan]Step 1/3: Extracting data...[/bold cyan]")
    data_file = output_dir / 'google_ads_data.json'

    try:
        extractor = GoogleAdsExtractor(credentials, customer_id)
        data = extractor.extract_all_data(days)
        extractor.export_to_json(data, str(data_file))
        console.print("✅ Data extraction complete\n")
    except Exception as e:
        console.print(f"[bold red]❌ Extraction failed: {e}[/bold red]")
        sys.exit(1)

    # Step 2: Analyze
    console.print("[bold cyan]Step 2/3: Analyzing data...[/bold cyan]")
    analysis_file = output_dir / 'analysis_report.json'

    try:
        analyzer = GoogleAdsAnalyzer(str(data_file))
        report = analyzer.generate_full_report(str(analysis_file))
        console.print("✅ Analysis complete\n")
    except Exception as e:
        console.print(f"[bold red]❌ Analysis failed: {e}[/bold red]")
        sys.exit(1)

    # Step 3: Generate summary report
    console.print("[bold cyan]Step 3/3: Generating summary report...[/bold cyan]")

    try:
        summary_file = output_dir / 'EXECUTIVE_SUMMARY.txt'

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write(f"GOOGLE ADS AUDIT - {client_name.upper()}\n")
            f.write("="*70 + "\n\n")

            exec_summary = report['executive_summary']
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 70 + "\n")
            f.write(f"Current ROAS: {exec_summary['current_roas']:.2f}\n")
            f.write(f"Forecasted ROAS: {exec_summary['forecasted_roas']:.2f}\n")
            f.write(f"Improvement Potential: +{exec_summary['improvement_potential']:.1f}%\n")
            f.write(f"Total Spend: €{exec_summary['total_spend']:,.2f}\n")
            f.write(f"Total Revenue: €{exec_summary['total_revenue']:,.2f}\n")
            f.write(f"Critical Issues: {exec_summary['critical_issues_count']}\n\n")

            f.write("PRIORITY RECOMMENDATIONS\n")
            f.write("-" * 70 + "\n")
            for i, rec in enumerate(report['priority_recommendations'][:10], 1):
                f.write(f"\n{i}. [{rec['priority']}] {rec['category']}\n")
                f.write(f"   Action: {rec['action']}\n")
                f.write(f"   Impact: {rec['expected_impact']} | Effort: {rec['effort']}\n")
                f.write(f"   Timeline: {rec['timeline']}\n")

        console.print("✅ Summary report generated\n")

        console.print("[bold green]🎉 Full audit complete![/bold green]\n")
        console.print(f"📊 All reports saved to: [cyan]{output_dir}[/cyan]\n")

        # Display final summary
        console.print(Panel.fit(
            f"[bold]ROAS:[/bold] {exec_summary['current_roas']:.2f} → {exec_summary['forecasted_roas']:.2f}\n"
            f"[bold]Improvement:[/bold] +{exec_summary['improvement_potential']:.1f}%\n"
            f"[bold]Revenue:[/bold] €{exec_summary['total_revenue']:,.2f}",
            title=f"[bold green]{client_name} - Summary[/bold green]",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[bold red]❌ Report generation failed: {e}[/bold red]")
        sys.exit(1)


@cli.command()
def setup():
    """Setup wizard for Google Ads API credentials"""

    console.print(Panel.fit(
        "⚙️ [bold blue]Google Ads API Setup Wizard[/bold blue]",
        border_style="blue"
    ))

    console.print("\n[yellow]This wizard will help you set up your Google Ads API credentials.[/yellow]\n")

    console.print("You'll need:")
    console.print("  1. Developer token")
    console.print("  2. Client ID")
    console.print("  3. Client secret")
    console.print("  4. Refresh token")
    console.print("  5. Customer ID\n")

    console.print("[cyan]For detailed instructions, visit:[/cyan]")
    console.print("https://developers.google.com/google-ads/api/docs/first-call/overview\n")

    # Create sample config
    sample_config = """# Google Ads API Configuration
# Replace with your actual credentials

developer_token: INSERT_DEVELOPER_TOKEN_HERE
client_id: INSERT_CLIENT_ID_HERE
client_secret: INSERT_CLIENT_SECRET_HERE
refresh_token: INSERT_REFRESH_TOKEN_HERE
login_customer_id: INSERT_LOGIN_CUSTOMER_ID_HERE
use_proto_plus: True
"""

    config_path = Path('config/google-ads.yaml')
    config_path.parent.mkdir(exist_ok=True)

    with open(config_path, 'w') as f:
        f.write(sample_config)

    console.print(f"[green]✅ Sample config created at:[/green] [cyan]{config_path}[/cyan]")
    console.print("\n[yellow]Please edit this file with your actual credentials.[/yellow]\n")


if __name__ == '__main__':
    cli()
