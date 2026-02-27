"""
Content Scrapers for AI News
Scrapes content from Reddit, NewsAPI, and Twitter
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from config import (
    SOURCES,
    REDDIT_CONFIG,
    NEWS_API_CONFIG,
    TWITTER_CONFIG,
    RATE_LIMITS,
)

logger = logging.getLogger(__name__)


class BaseScraper:
    """Base class for all scrapers"""

    def __init__(self):
        self.scraped_count = 0
        self.error_count = 0

    def scrape(self) -> List[Dict]:
        """Override this method in subclasses"""
        raise NotImplementedError

    def log_stats(self):
        """Log scraping statistics"""
        logger.info(f"{self.__class__.__name__}: Scraped {self.scraped_count} items, {self.error_count} errors")


class RedditScraper(BaseScraper):
    """Scrape AI news from Reddit"""

    def __init__(self):
        super().__init__()
        self.config = SOURCES['reddit']
        self.enabled = self.config['enabled']

        if self.enabled:
            try:
                import praw
                self.reddit = praw.Reddit(
                    client_id=REDDIT_CONFIG['client_id'],
                    client_secret=REDDIT_CONFIG['client_secret'],
                    user_agent=REDDIT_CONFIG['user_agent'],
                )
                logger.info("✅ Reddit scraper initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Reddit scraper: {e}")
                self.enabled = False
        else:
            logger.info("⏭️  Reddit scraper disabled (no credentials)")

    def scrape(self) -> List[Dict]:
        """Scrape posts from configured subreddits"""
        if not self.enabled:
            return []

        posts = []

        try:
            import praw

            for subreddit_name in self.config['subreddits']:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)

                    # Get top posts from specified time period
                    for submission in subreddit.top(
                        time_filter=self.config['time_filter'],
                        limit=self.config['limit']
                    ):
                        # Filter by minimum upvotes
                        if submission.score < self.config['min_upvotes']:
                            continue

                        # Skip stickied posts
                        if submission.stickied:
                            continue

                        post = {
                            'source': 'reddit',
                            'subreddit': subreddit_name,
                            'title': submission.title,
                            'content': submission.selftext[:500] if submission.selftext else '',
                            'url': submission.url if not submission.is_self else f"https://reddit.com{submission.permalink}",
                            'timestamp': datetime.fromtimestamp(submission.created_utc),
                            'engagement_score': submission.score,
                            'author': str(submission.author) if submission.author else '[deleted]',
                            'num_comments': submission.num_comments,
                        }

                        posts.append(post)
                        self.scraped_count += 1

                    # Rate limiting
                    time.sleep(RATE_LIMITS['reddit']['delay_between_requests'])

                    logger.debug(f"Scraped {len(posts)} posts from r/{subreddit_name}")

                except Exception as e:
                    logger.error(f"Error scraping r/{subreddit_name}: {e}")
                    self.error_count += 1

            logger.info(f"✅ Reddit: Scraped {len(posts)} posts from {len(self.config['subreddits'])} subreddits")

        except Exception as e:
            logger.error(f"❌ Reddit scraping failed: {e}")
            self.error_count += 1

        return posts


class NewsAPIScraper(BaseScraper):
    """Scrape AI news from NewsAPI"""

    def __init__(self):
        super().__init__()
        self.config = SOURCES['news_api']
        self.enabled = self.config['enabled']
        self.api_key = NEWS_API_CONFIG['api_key']
        self.base_url = NEWS_API_CONFIG['base_url']

        if self.enabled:
            logger.info("✅ NewsAPI scraper initialized")
        else:
            logger.info("⏭️  NewsAPI scraper disabled (no API key)")

    def scrape(self) -> List[Dict]:
        """Scrape articles from NewsAPI"""
        if not self.enabled:
            return []

        articles = []

        try:
            for query in self.config['search_queries']:
                try:
                    # Calculate date range (last 24 hours)
                    to_date = datetime.now()
                    from_date = to_date - timedelta(days=1)

                    # Build API request
                    params = {
                        'q': query,
                        'apiKey': self.api_key,
                        'language': self.config['language'],
                        'sortBy': self.config['sort_by'],
                        'pageSize': self.config['page_size'],
                        'from': from_date.isoformat(),
                        'to': to_date.isoformat(),
                    }

                    response = requests.get(
                        f"{self.base_url}/everything",
                        params=params,
                        timeout=10
                    )

                    if response.status_code == 200:
                        data = response.json()

                        for article in data.get('articles', []):
                            # Skip removed articles
                            if article.get('title') == '[Removed]':
                                continue

                            post = {
                                'source': 'newsapi',
                                'news_source': article['source']['name'],
                                'title': article['title'],
                                'content': article.get('description', '') or article.get('content', '')[:500],
                                'url': article['url'],
                                'timestamp': datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                                'author': article.get('author', 'Unknown'),
                                'engagement_score': 0,  # NewsAPI doesn't provide engagement metrics
                            }

                            articles.append(post)
                            self.scraped_count += 1

                    elif response.status_code == 426:
                        logger.error("❌ NewsAPI: Upgrade required or rate limit exceeded")
                        break
                    else:
                        logger.warning(f"NewsAPI request failed: {response.status_code} for query '{query}'")
                        self.error_count += 1

                    # Rate limiting
                    time.sleep(RATE_LIMITS['news_api']['delay_between_requests'])

                except Exception as e:
                    logger.error(f"Error scraping NewsAPI query '{query}': {e}")
                    self.error_count += 1

            logger.info(f"✅ NewsAPI: Scraped {len(articles)} articles")

        except Exception as e:
            logger.error(f"❌ NewsAPI scraping failed: {e}")
            self.error_count += 1

        return articles


class TwitterScraper(BaseScraper):
    """Scrape AI news from Twitter using Twitter API v2"""

    def __init__(self):
        super().__init__()
        self.config = SOURCES['twitter']
        self.enabled = self.config['enabled']

        if self.enabled:
            try:
                import tweepy

                self.client = tweepy.Client(
                    bearer_token=TWITTER_CONFIG['bearer_token'],
                    consumer_key=TWITTER_CONFIG['api_key'],
                    consumer_secret=TWITTER_CONFIG['api_secret'],
                    access_token=TWITTER_CONFIG['access_token'],
                    access_token_secret=TWITTER_CONFIG['access_secret'],
                )
                logger.info("✅ Twitter scraper initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Twitter scraper: {e}")
                self.enabled = False
        else:
            logger.info("⏭️  Twitter scraper disabled (no credentials)")

    def scrape(self) -> List[Dict]:
        """Scrape tweets from Twitter"""
        if not self.enabled:
            return []

        tweets = []

        try:
            import tweepy

            for query in self.config['search_queries']:
                try:
                    # Search recent tweets
                    response = self.client.search_recent_tweets(
                        query=query,
                        max_results=self.config['max_results'],
                        tweet_fields=['created_at', 'author_id', 'public_metrics', 'entities'],
                        expansions=['author_id'],
                    )

                    if response.data:
                        # Create user lookup dict
                        users = {user.id: user for user in response.includes.get('users', [])}

                        for tweet in response.data:
                            # Get author info
                            author = users.get(tweet.author_id)
                            author_name = author.username if author else 'unknown'

                            # Calculate engagement score
                            metrics = tweet.public_metrics
                            engagement = (
                                metrics['retweet_count'] * 2 +
                                metrics['like_count'] +
                                metrics['reply_count']
                            )

                            # Extract URLs
                            url = f"https://twitter.com/{author_name}/status/{tweet.id}"

                            post = {
                                'source': 'twitter',
                                'title': tweet.text[:100],  # First 100 chars as title
                                'content': tweet.text,
                                'url': url,
                                'timestamp': tweet.created_at,
                                'engagement_score': engagement,
                                'author': author_name,
                                'retweets': metrics['retweet_count'],
                                'likes': metrics['like_count'],
                            }

                            tweets.append(post)
                            self.scraped_count += 1

                    # Rate limiting
                    time.sleep(RATE_LIMITS['twitter']['delay_between_requests'])

                except tweepy.errors.TweepyException as e:
                    logger.error(f"Error scraping Twitter query '{query}': {e}")
                    self.error_count += 1

            logger.info(f"✅ Twitter: Scraped {len(tweets)} tweets")

        except Exception as e:
            logger.error(f"❌ Twitter scraping failed: {e}")
            self.error_count += 1

        return tweets


class CompoundScraper:
    """
    Compound scraper that coordinates all individual scrapers
    """

    def __init__(self):
        self.scrapers = []

        # Initialize enabled scrapers
        reddit = RedditScraper()
        if reddit.enabled:
            self.scrapers.append(reddit)

        newsapi = NewsAPIScraper()
        if newsapi.enabled:
            self.scrapers.append(newsapi)

        twitter = TwitterScraper()
        if twitter.enabled:
            self.scrapers.append(twitter)

        logger.info(f"Initialized {len(self.scrapers)} scrapers")

    def scrape_all(self) -> List[Dict]:
        """
        Run all enabled scrapers and combine results

        Returns:
            List of all scraped posts from all sources
        """
        all_posts = []

        logger.info(f"🔍 Starting scraping from {len(self.scrapers)} sources...")

        for scraper in self.scrapers:
            try:
                posts = scraper.scrape()
                all_posts.extend(posts)
                scraper.log_stats()
            except Exception as e:
                logger.error(f"Scraper {scraper.__class__.__name__} failed: {e}")

        logger.info(f"✅ Total scraped: {len(all_posts)} posts from all sources")

        return all_posts

    def scrape_by_source(self, source: str) -> List[Dict]:
        """
        Scrape from a specific source only

        Args:
            source: 'reddit', 'newsapi', or 'twitter'

        Returns:
            List of posts from that source
        """
        scraper_map = {
            'reddit': RedditScraper,
            'newsapi': NewsAPIScraper,
            'twitter': TwitterScraper,
        }

        scraper_class = scraper_map.get(source.lower())
        if not scraper_class:
            logger.error(f"Unknown source: {source}")
            return []

        scraper = scraper_class()
        if not scraper.enabled:
            logger.warning(f"{source} scraper is not enabled")
            return []

        return scraper.scrape()


def test_scrapers():
    """Test function to verify scrapers are working"""
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 60)
    print("AI NEWS SCRAPER TEST")
    print("=" * 60 + "\n")

    scraper = CompoundScraper()

    if not scraper.scrapers:
        print("❌ No scrapers enabled!")
        print("\nPlease configure at least one of:")
        print("  - Reddit (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)")
        print("  - NewsAPI (NEWS_API_KEY)")
        print("  - Twitter (TWITTER_BEARER_TOKEN)")
        sys.exit(1)

    print(f"✅ {len(scraper.scrapers)} scraper(s) enabled\n")

    # Test scraping
    posts = scraper.scrape_all()

    print("\n" + "=" * 60)
    print(f"RESULTS: {len(posts)} total posts")
    print("=" * 60 + "\n")

    if posts:
        # Show sample posts
        print("Sample posts:\n")
        for i, post in enumerate(posts[:3], 1):
            print(f"{i}. [{post['source']}] {post['title'][:60]}...")
            print(f"   URL: {post['url']}")
            print(f"   Engagement: {post.get('engagement_score', 0)}")
            print()

        # Source breakdown
        from collections import Counter
        source_counts = Counter(p['source'] for p in posts)
        print("Posts by source:")
        for source, count in source_counts.items():
            print(f"  {source}: {count}")

    else:
        print("⚠️  No posts scraped. This could mean:")
        print("  - API credentials are invalid")
        print("  - No content matches the search criteria")
        print("  - Rate limits have been exceeded")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_scrapers()
