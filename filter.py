"""
Content Filter for AI News
Scores and filters scraped content for relevance
"""

import logging
import re
from typing import List, Dict, Set
from datetime import datetime, timedelta
from config import (
    FILTER_CONFIG,
    AI_COMPANIES,
    get_all_company_keywords,
    get_high_priority_companies,
)

logger = logging.getLogger(__name__)


class ContentFilter:
    """Filter and score content for relevance to AI news"""

    def __init__(self):
        self.min_relevance = FILTER_CONFIG['min_relevance_score']
        self.exclude_keywords = [kw.lower() for kw in FILTER_CONFIG['exclude_keywords']]
        self.require_keywords = [kw.lower() for kw in FILTER_CONFIG['require_keywords']]
        self.company_keywords = [kw.lower() for kw in get_all_company_keywords()]
        self.high_priority_companies = [c.lower() for c in get_high_priority_companies()]

        logger.info(f"Content filter initialized (min relevance: {self.min_relevance})")

    def score_relevance(self, post: Dict) -> float:
        """
        Calculate relevance score for a post

        Args:
            post: Dictionary containing post data

        Returns:
            Relevance score between 0.0 and 1.0
        """
        score = 0.0
        text = f"{post.get('title', '')} {post.get('content', '')}".lower()

        # 1. Company mentions (0-0.35 points)
        company_score = self._score_company_mentions(text)
        score += company_score

        # 2. Required keywords (0-0.25 points)
        keyword_score = self._score_keywords(text)
        score += keyword_score

        # 3. Engagement metrics (0-0.2 points)
        engagement_score = self._score_engagement(post)
        score += engagement_score

        # 4. Content freshness (0-0.1 points)
        freshness_score = self._score_freshness(post)
        score += freshness_score

        # 5. Content quality (0-0.1 points)
        quality_score = self._score_quality(post)
        score += quality_score

        # Penalties
        penalty = self._calculate_penalties(text)
        score = max(0.0, score - penalty)

        # Normalize to 0-1 range
        final_score = min(1.0, score)

        logger.debug(f"Post scored {final_score:.2f}: {post.get('title', '')[:50]}...")
        return final_score

    def _score_company_mentions(self, text: str) -> float:
        """Score based on AI company mentions (max 0.35)"""
        score = 0.0

        # Check for high-priority companies (OpenAI, Anthropic, Google DeepMind)
        high_priority_mentions = sum(
            1 for company in self.high_priority_companies
            if company in text
        )
        score += min(0.25, high_priority_mentions * 0.15)

        # Check for any company mentions
        company_mentions = sum(
            1 for keyword in self.company_keywords
            if keyword in text
        )
        score += min(0.1, company_mentions * 0.05)

        return score

    def _score_keywords(self, text: str) -> float:
        """Score based on required keywords (max 0.25)"""
        score = 0.0

        # Count matches from required keywords
        matches = sum(
            1 for keyword in self.require_keywords
            if keyword in text
        )

        # More matches = higher score
        if matches >= 5:
            score = 0.25
        elif matches >= 3:
            score = 0.15
        elif matches >= 1:
            score = 0.1

        return score

    def _score_engagement(self, post: Dict) -> float:
        """Score based on engagement metrics (max 0.2)"""
        engagement = post.get('engagement_score', 0)
        source = post.get('source', '')

        # Different thresholds for different platforms
        if source == 'reddit':
            # Reddit scores (upvotes)
            if engagement >= 500:
                return 0.2
            elif engagement >= 200:
                return 0.15
            elif engagement >= 50:
                return 0.1
            elif engagement >= 10:
                return 0.05

        elif source == 'twitter':
            # Twitter engagement (likes + retweets)
            if engagement >= 1000:
                return 0.2
            elif engagement >= 500:
                return 0.15
            elif engagement >= 100:
                return 0.1
            elif engagement >= 10:
                return 0.05

        elif source == 'newsapi':
            # NewsAPI doesn't have engagement metrics
            # Give baseline score for being from news source
            return 0.05

        return 0.0

    def _score_freshness(self, post: Dict) -> float:
        """Score based on content recency (max 0.1)"""
        timestamp = post.get('timestamp')
        if not timestamp:
            return 0.0

        # Convert to datetime if needed
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except:
                return 0.0

        # Calculate age in hours
        now = datetime.now()
        if timestamp.tzinfo:
            import pytz
            now = pytz.utc.localize(now)

        age_hours = (now - timestamp).total_seconds() / 3600

        # Fresher content scores higher
        if age_hours <= 6:
            return 0.1
        elif age_hours <= 12:
            return 0.07
        elif age_hours <= 24:
            return 0.05
        elif age_hours <= 48:
            return 0.03

        return 0.0

    def _score_quality(self, post: Dict) -> float:
        """Score based on content quality indicators (max 0.1)"""
        score = 0.0

        title = post.get('title', '')
        content = post.get('content', '')

        # Title quality
        if len(title) >= 20 and len(title) <= 150:
            score += 0.03

        # Has substantial content
        if len(content) >= 100:
            score += 0.03

        # Not clickbait indicators
        clickbait_patterns = [
            r'you won\'t believe',
            r'shocking',
            r'one weird trick',
            r'doctors hate',
            r'\?{3,}',  # Multiple question marks
            r'!{3,}',  # Multiple exclamation marks
        ]

        is_clickbait = any(
            re.search(pattern, title.lower())
            for pattern in clickbait_patterns
        )

        if not is_clickbait:
            score += 0.04

        return score

    def _calculate_penalties(self, text: str) -> float:
        """Calculate penalty for excluded content"""
        penalty = 0.0

        # Check for excluded keywords
        for keyword in self.exclude_keywords:
            if keyword in text:
                penalty += 0.2  # Heavy penalty

        return penalty

    def filter_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        Filter posts by relevance score

        Args:
            posts: List of post dictionaries

        Returns:
            Filtered and sorted list of posts
        """
        logger.info(f"Filtering {len(posts)} posts...")

        # Score all posts
        scored_posts = []
        for post in posts:
            score = self.score_relevance(post)
            post['relevance_score'] = score

            if score >= self.min_relevance:
                scored_posts.append(post)

        # Sort by relevance score (descending)
        scored_posts.sort(key=lambda p: p['relevance_score'], reverse=True)

        # Limit to max posts per cycle
        max_posts = FILTER_CONFIG['max_posts_per_cycle']
        filtered_posts = scored_posts[:max_posts]

        logger.info(f"✅ Filtered to {len(filtered_posts)} relevant posts (min score: {self.min_relevance})")

        return filtered_posts

    def get_company_mentions(self, post: Dict) -> str:
        """
        Extract company mentions from post

        Args:
            post: Post dictionary

        Returns:
            Comma-separated string of mentioned companies
        """
        text = f"{post.get('title', '')} {post.get('content', '')}".lower()
        mentioned_companies = []

        # Check all companies
        for region, companies in AI_COMPANIES.items():
            for company in companies:
                company_name = company['name']
                keywords = [kw.lower() for kw in company['keywords']]

                # Check if any keyword is in text
                if any(keyword in text for keyword in keywords):
                    mentioned_companies.append(company_name)

        return ', '.join(mentioned_companies)

    def deduplicate_posts(self, posts: List[Dict]) -> List[Dict]:
        """
        Remove duplicate posts based on URL and similar titles

        Args:
            posts: List of post dictionaries

        Returns:
            Deduplicated list
        """
        seen_urls = set()
        seen_titles = set()
        unique_posts = []

        for post in posts:
            url = post.get('url', '')
            title = post.get('title', '').lower()

            # Skip if URL already seen
            if url and url in seen_urls:
                continue

            # Skip if very similar title seen
            title_words = set(title.split())
            is_duplicate = False

            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                # If 80%+ words match, consider duplicate
                if len(title_words & seen_words) / max(len(title_words), 1) > 0.8:
                    is_duplicate = True
                    break

            if is_duplicate:
                continue

            # Add to unique posts
            seen_urls.add(url)
            seen_titles.add(title)
            unique_posts.append(post)

        removed = len(posts) - len(unique_posts)
        if removed > 0:
            logger.info(f"Removed {removed} duplicate posts")

        return unique_posts

    def analyze_posts(self, posts: List[Dict]) -> Dict:
        """
        Analyze filtered posts and return statistics

        Args:
            posts: List of post dictionaries

        Returns:
            Dictionary with analysis results
        """
        from collections import Counter

        analysis = {
            'total_posts': len(posts),
            'avg_relevance': 0.0,
            'sources': Counter(),
            'companies': Counter(),
            'top_posts': [],
        }

        if not posts:
            return analysis

        # Calculate average relevance
        total_relevance = sum(p.get('relevance_score', 0) for p in posts)
        analysis['avg_relevance'] = total_relevance / len(posts)

        # Count sources
        for post in posts:
            source = post.get('source', 'unknown')
            analysis['sources'][source] += 1

        # Extract company mentions
        for post in posts:
            companies = self.get_company_mentions(post)
            if companies:
                for company in companies.split(', '):
                    analysis['companies'][company] += 1

        # Get top posts
        sorted_posts = sorted(
            posts,
            key=lambda p: p.get('relevance_score', 0),
            reverse=True
        )
        analysis['top_posts'] = sorted_posts[:5]

        return analysis


if __name__ == "__main__":
    # Test filter
    logging.basicConfig(level=logging.INFO)

    # Sample posts for testing
    test_posts = [
        {
            'title': 'OpenAI Announces GPT-5 with Revolutionary Capabilities',
            'content': 'OpenAI today announced the release of GPT-5, their latest large language model...',
            'url': 'https://example.com/gpt5',
            'source': 'newsapi',
            'timestamp': datetime.now(),
            'engagement_score': 500,
        },
        {
            'title': 'Anthropic Raises $1B for Claude Development',
            'content': 'Anthropic announced a major funding round to expand Claude AI capabilities...',
            'url': 'https://example.com/anthropic',
            'source': 'reddit',
            'timestamp': datetime.now() - timedelta(hours=3),
            'engagement_score': 250,
        },
        {
            'title': 'Random Tech News',
            'content': 'Some random technology news without AI focus...',
            'url': 'https://example.com/random',
            'source': 'newsapi',
            'timestamp': datetime.now() - timedelta(days=2),
            'engagement_score': 10,
        },
    ]

    filter_obj = ContentFilter()

    print("\n" + "=" * 60)
    print("CONTENT FILTER TEST")
    print("=" * 60 + "\n")

    filtered = filter_obj.filter_posts(test_posts)

    print(f"Filtered {len(filtered)} / {len(test_posts)} posts\n")

    for i, post in enumerate(filtered, 1):
        print(f"{i}. {post['title']}")
        print(f"   Score: {post['relevance_score']:.2f}")
        print(f"   Companies: {filter_obj.get_company_mentions(post)}")
        print()

    # Analysis
    analysis = filter_obj.analyze_posts(filtered)
    print("Analysis:")
    print(f"  Average relevance: {analysis['avg_relevance']:.2f}")
    print(f"  Sources: {dict(analysis['sources'])}")
    print(f"  Companies: {dict(analysis['companies'])}")
