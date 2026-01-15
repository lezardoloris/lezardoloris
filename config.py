"""
Configuration module for AI News Scraper
Centralized configuration for all components
"""

import os
from dotenv import load_dotenv
from datetime import datetime, time

# Load environment variables
load_dotenv()

# ============================================
# API CREDENTIALS
# ============================================

# Metricool (REQUIRED)
METRICOOL_CONFIG = {
    'token': os.getenv('METRICOOL_TOKEN', ''),
    'user_id': os.getenv('METRICOOL_USER_ID', ''),
    'blog_id': os.getenv('METRICOOL_BLOG_ID', ''),
}

# NewsAPI (REQUIRED)
NEWS_API_CONFIG = {
    'api_key': os.getenv('NEWS_API_KEY', ''),
    'base_url': 'https://newsapi.org/v2',
}

# Reddit (OPTIONAL)
REDDIT_CONFIG = {
    'client_id': os.getenv('REDDIT_CLIENT_ID', ''),
    'client_secret': os.getenv('REDDIT_CLIENT_SECRET', ''),
    'user_agent': os.getenv('REDDIT_USER_AGENT', 'AI News Scraper v1.0'),
}

# Twitter API v2 (OPTIONAL - Requires paid tier)
TWITTER_CONFIG = {
    'api_key': os.getenv('TWITTER_API_KEY', ''),
    'api_secret': os.getenv('TWITTER_API_SECRET', ''),
    'bearer_token': os.getenv('TWITTER_BEARER_TOKEN', ''),
    'access_token': os.getenv('TWITTER_ACCESS_TOKEN', ''),
    'access_secret': os.getenv('TWITTER_ACCESS_SECRET', ''),
}

# ============================================
# DATABASE CONFIGURATION
# ============================================

DATABASE_CONFIG = {
    'db_path': os.getenv('DATABASE_PATH', 'ai_news.db'),
    'cleanup_days': 30,  # Delete posts older than 30 days
}

# ============================================
# SCRAPING SOURCES
# ============================================

SOURCES = {
    'reddit': {
        'enabled': bool(REDDIT_CONFIG['client_id']),
        'subreddits': [
            'OpenAI',
            'MachineLearning',
            'LanguageModels',
            'ArtificialIntelligence',
            'deeplearning',
            'LocalLLaMA',
            'Anthropic',
            'GoogleGemini',
        ],
        'limit': 50,  # Posts per subreddit
        'time_filter': 'day',  # day, week, month
        'min_upvotes': 10,
    },
    'news_api': {
        'enabled': bool(NEWS_API_CONFIG['api_key']),
        'search_queries': [
            'OpenAI',
            'ChatGPT',
            'GPT-4',
            'Anthropic Claude',
            'Google Gemini',
            'DeepMind',
            'Meta AI',
            'LLaMA',
            'artificial intelligence breakthrough',
            'AI research',
            'large language model',
        ],
        'language': 'en',
        'sort_by': 'relevancy',  # relevancy, popularity, publishedAt
        'page_size': 20,
    },
    'twitter': {
        'enabled': bool(TWITTER_CONFIG['bearer_token']),
        'search_queries': [
            '#OpenAI',
            '#ChatGPT',
            '#Claude',
            '#Gemini',
            '#AI',
            'from:OpenAI',
            'from:AnthropicAI',
            'from:GoogleAI',
            'from:MetaAI',
        ],
        'max_results': 30,
    },
}

# ============================================
# AI COMPANIES TO TRACK
# ============================================

AI_COMPANIES = {
    'US/Global': [
        {
            'name': 'OpenAI',
            'keywords': ['OpenAI', 'ChatGPT', 'GPT-4', 'GPT-5', 'Sam Altman', 'Sora'],
            'priority': 'high',
        },
        {
            'name': 'Anthropic',
            'keywords': ['Anthropic', 'Claude', 'Claude 3', 'Claude 4', 'Dario Amodei'],
            'priority': 'high',
        },
        {
            'name': 'Google DeepMind',
            'keywords': ['Google DeepMind', 'Gemini', 'Bard', 'AlphaFold', 'Demis Hassabis'],
            'priority': 'high',
        },
        {
            'name': 'Meta AI',
            'keywords': ['Meta AI', 'LLaMA', 'Llama', 'PyTorch', 'Yann LeCun'],
            'priority': 'medium',
        },
        {
            'name': 'Microsoft',
            'keywords': ['Microsoft AI', 'Copilot', 'Azure AI', 'Bing AI'],
            'priority': 'medium',
        },
        {
            'name': 'xAI',
            'keywords': ['xAI', 'Grok', 'Elon Musk AI'],
            'priority': 'medium',
        },
        {
            'name': 'Perplexity',
            'keywords': ['Perplexity AI', 'Perplexity'],
            'priority': 'low',
        },
    ],
    'Europe': [
        {
            'name': 'Mistral AI',
            'keywords': ['Mistral AI', 'Mistral', 'Mixtral'],
            'priority': 'medium',
        },
        {
            'name': 'Aleph Alpha',
            'keywords': ['Aleph Alpha', 'Luminous'],
            'priority': 'low',
        },
    ],
    'Asia': [
        {
            'name': 'Baidu',
            'keywords': ['Baidu AI', 'ERNIE Bot'],
            'priority': 'low',
        },
        {
            'name': 'Alibaba',
            'keywords': ['Alibaba AI', 'Qwen', 'Tongyi Qianwen'],
            'priority': 'low',
        },
    ],
}

# ============================================
# CONTENT FILTERING
# ============================================

FILTER_CONFIG = {
    'min_relevance_score': 0.6,  # 0-1 scale
    'max_posts_per_cycle': 10,
    'exclude_keywords': [
        'nsfw',
        'explicit',
        'leaked',
        'rumor',
        'unconfirmed',
    ],
    'require_keywords': [
        'release',
        'launch',
        'announce',
        'breakthrough',
        'research',
        'update',
        'model',
        'AI',
        'LLM',
        'GPT',
        'Claude',
        'Gemini',
    ],
}

# ============================================
# TWEET GENERATION
# ============================================

TWEET_CONFIG = {
    'max_length': 280,
    'include_hashtags': True,
    'hashtags': ['#AI', '#ArtificialIntelligence', '#MachineLearning', '#LLM'],
    'include_url': True,
    'emojis_enabled': True,
    'emoji_map': {
        'release': '🚀',
        'announce': '📢',
        'breakthrough': '💡',
        'research': '🔬',
        'update': '🆕',
        'model': '🤖',
        'warning': '⚠️',
        'success': '✅',
    },
    'templates': [
        "{emoji} {headline}\n\n{summary}\n\n{url} {hashtags}",
        "{emoji} NEW: {headline}\n{summary}\n\n🔗 {url}\n{hashtags}",
        "{headline} {emoji}\n\n{summary}\n\nRead more: {url}\n{hashtags}",
    ],
}

# ============================================
# SCHEDULING CONFIGURATION
# ============================================

TIMEZONE_CONFIG = {
    'posting_timezone': os.getenv('POSTING_TIMEZONE', 'America/New_York'),
    'post_hours': [9, 14, 18],  # 9 AM, 2 PM, 6 PM EST
    'skip_weekends': False,
    'max_posts_per_day': 5,
}

# ============================================
# LOGGING CONFIGURATION
# ============================================

LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'log_file': os.getenv('LOG_FILE', 'ai_news_scraper.log'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
}

# ============================================
# RATE LIMITING
# ============================================

RATE_LIMITS = {
    'reddit': {
        'requests_per_minute': 60,
        'delay_between_requests': 1,  # seconds
    },
    'news_api': {
        'requests_per_day': 100,  # Free tier limit
        'delay_between_requests': 2,
    },
    'twitter': {
        'requests_per_15_min': 180,  # Depends on tier
        'delay_between_requests': 1,
    },
    'metricool': {
        'posts_per_day': 100,
        'delay_between_posts': 0.5,
    },
}

# ============================================
# VALIDATION
# ============================================

def validate_config():
    """Validate that required configuration is present"""
    errors = []

    # Check Metricool (required)
    if not METRICOOL_CONFIG['token']:
        errors.append("METRICOOL_TOKEN is required")
    if not METRICOOL_CONFIG['user_id']:
        errors.append("METRICOOL_USER_ID is required")
    if not METRICOOL_CONFIG['blog_id']:
        errors.append("METRICOOL_BLOG_ID is required")

    # Check NewsAPI (required)
    if not NEWS_API_CONFIG['api_key']:
        errors.append("NEWS_API_KEY is required")

    # Warn about optional services
    warnings = []
    if not REDDIT_CONFIG['client_id']:
        warnings.append("Reddit credentials not configured (optional)")
    if not TWITTER_CONFIG['bearer_token']:
        warnings.append("Twitter credentials not configured (optional)")

    return errors, warnings


def get_all_company_keywords():
    """Get flat list of all company keywords for filtering"""
    keywords = []
    for region, companies in AI_COMPANIES.items():
        for company in companies:
            keywords.extend(company['keywords'])
    return list(set(keywords))  # Remove duplicates


def get_high_priority_companies():
    """Get list of high priority company names"""
    companies = []
    for region, company_list in AI_COMPANIES.items():
        for company in company_list:
            if company.get('priority') == 'high':
                companies.append(company['name'])
    return companies


if __name__ == "__main__":
    # Test configuration validation
    errors, warnings = validate_config()

    print("Configuration Validation:")
    print("=" * 50)

    if errors:
        print("\nERRORS (must fix):")
        for error in errors:
            print(f"  ❌ {error}")
    else:
        print("\n✅ No errors - required configuration is valid")

    if warnings:
        print("\nWARNINGS (optional):")
        for warning in warnings:
            print(f"  ⚠️  {warning}")

    print("\n" + "=" * 50)
    print(f"Enabled sources: {[k for k, v in SOURCES.items() if v['enabled']]}")
    print(f"Company keywords: {len(get_all_company_keywords())} total")
    print(f"High priority companies: {get_high_priority_companies()}")
