#!/usr/bin/env python3
"""
AI News Scraper - Main Orchestration Script
Coordinates scraping, filtering, tweet generation, and scheduling
"""

import logging
import sys
from datetime import datetime
from typing import List, Dict

# Import project modules
from database import NewsDatabase
from scrapers import CompoundScraper
from filter import ContentFilter
from tweet_generator import TweetGenerator
from metricool_api import MetricoolAPI, MetricoolScheduler
from config import (
    LOGGING_CONFIG,
    DATABASE_CONFIG,
    TIMEZONE_CONFIG,
    validate_config,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    datefmt=LOGGING_CONFIG['date_format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['log_file']),
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)


class AINewsPipeline:
    """Main pipeline for AI news scraping and scheduling"""

    def __init__(self):
        """Initialize all components"""
        logger.info("="*60)
        logger.info("AI NEWS SCRAPER - INITIALIZING")
        logger.info("="*60)

        # Validate configuration
        self._validate_config()

        # Initialize components
        self.db = NewsDatabase(DATABASE_CONFIG['db_path'])
        self.scraper = CompoundScraper()
        self.filter = ContentFilter()
        self.tweet_generator = TweetGenerator()
        self.metricool_api = MetricoolAPI()
        self.metricool_scheduler = MetricoolScheduler(self.metricool_api)

        logger.info("✅ All components initialized")

    def _validate_config(self):
        """Validate configuration before starting"""
        errors, warnings = validate_config()

        if errors:
            logger.error("❌ Configuration errors detected:")
            for error in errors:
                logger.error(f"  - {error}")
            logger.error("\nPlease check your .env file and fix these errors.")
            sys.exit(1)

        if warnings:
            logger.warning("⚠️  Configuration warnings:")
            for warning in warnings:
                logger.warning(f"  - {warning}")

    def run(self) -> Dict:
        """
        Execute the full pipeline

        Returns:
            Dictionary with execution results
        """
        logger.info("")
        logger.info("📅 STARTING DAILY AI NEWS CYCLE")
        logger.info("="*60)

        results = {
            'success': True,
            'timestamp': datetime.now(),
            'posts_scraped': 0,
            'posts_stored': 0,
            'posts_filtered': 0,
            'tweets_generated': 0,
            'tweets_scheduled': 0,
            'errors': [],
        }

        try:
            # Step 1: Scraping
            logger.info("")
            logger.info("[1/5] 🔍 SCRAPING CONTENT...")
            logger.info("-"*60)
            posts = self._scrape_content()
            results['posts_scraped'] = len(posts)

            if not posts:
                logger.warning("⚠️  No posts scraped. Check API credentials and rate limits.")
                results['success'] = False
                return results

            # Step 2: Database storage
            logger.info("")
            logger.info("[2/5] 💾 STORING IN DATABASE...")
            logger.info("-"*60)
            stored_count = self._store_posts(posts)
            results['posts_stored'] = stored_count

            # Step 3: Filtering
            logger.info("")
            logger.info("[3/5] 🎯 FILTERING FOR RELEVANCE...")
            logger.info("-"*60)
            filtered_posts = self._filter_content(posts)
            results['posts_filtered'] = len(filtered_posts)

            if not filtered_posts:
                logger.warning("⚠️  No relevant posts found. Consider lowering min_relevance_score.")
                results['success'] = False
                return results

            # Step 4: Tweet generation
            logger.info("")
            logger.info("[4/5] ✍️  GENERATING TWEETS...")
            logger.info("-"*60)
            tweets = self._generate_tweets(filtered_posts)
            results['tweets_generated'] = len(tweets)

            if not tweets:
                logger.error("❌ Failed to generate tweets")
                results['success'] = False
                return results

            # Step 5: Scheduling
            logger.info("")
            logger.info("[5/5] 📤 SCHEDULING VIA METRICOOL...")
            logger.info("-"*60)
            scheduled_count = self._schedule_tweets(tweets)
            results['tweets_scheduled'] = scheduled_count

            # Database cleanup
            self._cleanup_database()

            # Final summary
            self._print_summary(results)

        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}", exc_info=True)
            results['success'] = False
            results['errors'].append(str(e))

        return results

    def _scrape_content(self) -> List[Dict]:
        """Scrape content from all sources"""
        posts = self.scraper.scrape_all()
        logger.info(f"✅ Scraped {len(posts)} posts total")
        return posts

    def _store_posts(self, posts: List[Dict]) -> int:
        """Store posts in database"""
        stored_count = 0

        for post in posts:
            post_id = self.db.insert_post(post)
            if post_id:
                stored_count += 1

        logger.info(f"✅ Stored {stored_count} new posts (duplicates filtered)")
        return stored_count

    def _filter_content(self, posts: List[Dict]) -> List[Dict]:
        """Filter posts for relevance"""
        # Deduplicate first
        unique_posts = self.filter.deduplicate_posts(posts)

        # Filter by relevance
        filtered_posts = self.filter.filter_posts(unique_posts)

        # Add company mentions
        for post in filtered_posts:
            post['company_mentions'] = self.filter.get_company_mentions(post)

        # Show top posts
        logger.info("")
        logger.info("Top relevant posts:")
        for i, post in enumerate(filtered_posts[:5], 1):
            logger.info(f"  {i}. [{post['source']}] {post['title'][:60]}...")
            logger.info(f"     Score: {post['relevance_score']:.2f} | Companies: {post.get('company_mentions', 'N/A')}")

        return filtered_posts

    def _generate_tweets(self, posts: List[Dict]) -> List[Dict]:
        """Generate tweets from filtered posts"""
        max_tweets = min(
            len(posts),
            TIMEZONE_CONFIG['max_posts_per_day']
        )

        tweets = self.tweet_generator.generate_multiple_tweets(
            posts,
            max_tweets=max_tweets
        )

        # Preview tweets
        logger.info("")
        logger.info("Generated tweets:")
        for i, tweet in enumerate(tweets, 1):
            logger.info(f"  {i}. {tweet['text'][:60]}... ({len(tweet['text'])} chars)")

        return tweets

    def _schedule_tweets(self, tweets: List[Dict]) -> int:
        """Schedule tweets via Metricool"""
        # Prepare tweet data
        tweet_data = [
            {
                'text': t['text'],
                'media_urls': t.get('media_urls'),
            }
            for t in tweets
        ]

        # Schedule with optimal timing
        results = self.metricool_scheduler.schedule_tweets_optimally(
            tweets=tweet_data,
            target_hours=TIMEZONE_CONFIG['post_hours'],
            timezone_name=TIMEZONE_CONFIG['posting_timezone']
        )

        # Store scheduled tweets in database
        if results['success'] > 0:
            for i, tweet in enumerate(tweets[:results['success']]):
                scheduled_time = results['scheduled_times'][i]

                self.db.insert_tweet({
                    'tweet_text': tweet['text'],
                    'source_url': tweet['source_url'],
                    'source_post_id': tweet.get('source_post_id'),
                    'scheduled_time': scheduled_time,
                    'status': 'scheduled',
                })

        logger.info(f"✅ Scheduled {results['success']}/{len(tweets)} tweets")

        if results['failed'] > 0:
            logger.warning(f"⚠️  Failed to schedule {results['failed']} tweets")

        return results['success']

    def _cleanup_database(self):
        """Clean up old database records"""
        cleanup_days = DATABASE_CONFIG['cleanup_days']
        logger.info(f"🧹 Cleaning up posts older than {cleanup_days} days...")
        self.db.cleanup_old_posts(cleanup_days)

    def _print_summary(self, results: Dict):
        """Print execution summary"""
        logger.info("")
        logger.info("="*60)
        logger.info("📊 EXECUTION SUMMARY")
        logger.info("="*60)
        logger.info(f"Status: {'✅ SUCCESS' if results['success'] else '❌ FAILED'}")
        logger.info(f"Timestamp: {results['timestamp']}")
        logger.info("")
        logger.info(f"Posts scraped:      {results['posts_scraped']}")
        logger.info(f"Posts stored:       {results['posts_stored']}")
        logger.info(f"Posts filtered:     {results['posts_filtered']}")
        logger.info(f"Tweets generated:   {results['tweets_generated']}")
        logger.info(f"Tweets scheduled:   {results['tweets_scheduled']}")
        logger.info("="*60)

        # Database stats
        stats = self.db.get_stats()
        logger.info("")
        logger.info("📈 DATABASE STATISTICS")
        logger.info("-"*60)
        logger.info(f"Total posts:        {stats.get('total_posts', 0)}")
        logger.info(f"Total tweets:       {stats.get('total_tweets', 0)}")
        logger.info(f"Avg relevance:      {stats.get('avg_relevance', 0)}")
        logger.info("="*60)

    def test_apis(self) -> bool:
        """Test API connections"""
        logger.info("")
        logger.info("🧪 TESTING API CONNECTIONS")
        logger.info("="*60)

        all_ok = True

        # Test Metricool
        logger.info("Testing Metricool API...")
        if self.metricool_api.test_connection():
            logger.info("  ✅ Metricool API OK")
        else:
            logger.error("  ❌ Metricool API FAILED")
            all_ok = False

        # Test scrapers
        logger.info("Testing scrapers...")
        if self.scraper.scrapers:
            logger.info(f"  ✅ {len(self.scraper.scrapers)} scraper(s) enabled")
        else:
            logger.error("  ❌ No scrapers enabled")
            all_ok = False

        logger.info("="*60)

        return all_ok


def main():
    """Main entry point"""
    try:
        pipeline = AINewsPipeline()

        # Check if we should run test mode
        if len(sys.argv) > 1 and sys.argv[1] == '--test':
            logger.info("Running in TEST mode...")
            success = pipeline.test_apis()
            sys.exit(0 if success else 1)

        # Run the full pipeline
        results = pipeline.run()

        # Exit with appropriate code
        sys.exit(0 if results['success'] else 1)

    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Ensure database connection is closed
        try:
            pipeline.db.close()
        except:
            pass


if __name__ == "__main__":
    main()
