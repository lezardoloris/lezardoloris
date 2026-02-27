"""
Database layer for AI News Scraper
Handles storage and retrieval of scraped posts and scheduled tweets
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)


class NewsDatabase:
    """SQLite database manager for AI news scraper"""

    def __init__(self, db_path: str = "ai_news.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._initialize_database()

    def _initialize_database(self):
        """Create database tables if they don't exist"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()

            # Create scraped_posts table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraped_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    url TEXT NOT NULL UNIQUE,
                    timestamp DATETIME NOT NULL,
                    relevance_score REAL DEFAULT 0.0,
                    engagement_score INTEGER DEFAULT 0,
                    company_mentions TEXT,
                    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_duplicate BOOLEAN DEFAULT 0
                )
            """)

            # Create scheduled_tweets table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_tweets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tweet_text TEXT NOT NULL,
                    source_url TEXT,
                    source_post_id INTEGER,
                    scheduled_time DATETIME NOT NULL,
                    metricool_id TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    posted_at DATETIME,
                    FOREIGN KEY (source_post_id) REFERENCES scraped_posts(id)
                )
            """)

            # Create indices for performance
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_url ON scraped_posts(url)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_relevance ON scraped_posts(relevance_score)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON scraped_posts(timestamp)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_scheduled_time ON scheduled_tweets(scheduled_time)
            """)

            self.connection.commit()
            logger.info(f"Database initialized at {self.db_path}")

        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def insert_post(self, post_data: Dict) -> Optional[int]:
        """
        Insert a scraped post into database

        Args:
            post_data: Dictionary containing post information
                - source: str (reddit, newsapi, twitter)
                - title: str
                - content: str
                - url: str
                - timestamp: datetime
                - relevance_score: float (0-1)
                - engagement_score: int
                - company_mentions: str (comma-separated)

        Returns:
            Post ID if inserted, None if duplicate
        """
        try:
            # Check for duplicate URL
            if self.is_duplicate(post_data['url']):
                logger.debug(f"Duplicate URL detected: {post_data['url']}")
                return None

            self.cursor.execute("""
                INSERT INTO scraped_posts (
                    source, title, content, url, timestamp,
                    relevance_score, engagement_score, company_mentions
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_data['source'],
                post_data['title'],
                post_data.get('content', ''),
                post_data['url'],
                post_data['timestamp'],
                post_data.get('relevance_score', 0.0),
                post_data.get('engagement_score', 0),
                post_data.get('company_mentions', '')
            ))

            self.connection.commit()
            post_id = self.cursor.lastrowid
            logger.debug(f"Inserted post {post_id}: {post_data['title'][:50]}...")
            return post_id

        except sqlite3.IntegrityError:
            logger.warning(f"Integrity error inserting post: {post_data.get('url', 'unknown')}")
            return None
        except sqlite3.Error as e:
            logger.error(f"Error inserting post: {e}")
            return None

    def is_duplicate(self, url: str) -> bool:
        """Check if URL already exists in database"""
        try:
            self.cursor.execute(
                "SELECT id FROM scraped_posts WHERE url = ?",
                (url,)
            )
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"Error checking duplicate: {e}")
            return False

    def get_top_posts(self, limit: int = 10, min_relevance: float = 0.6) -> List[Dict]:
        """
        Get top posts by relevance score

        Args:
            limit: Maximum number of posts to return
            min_relevance: Minimum relevance score (0-1)

        Returns:
            List of post dictionaries
        """
        try:
            self.cursor.execute("""
                SELECT * FROM scraped_posts
                WHERE relevance_score >= ?
                ORDER BY relevance_score DESC, engagement_score DESC
                LIMIT ?
            """, (min_relevance, limit))

            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error getting top posts: {e}")
            return []

    def insert_tweet(self, tweet_data: Dict) -> Optional[int]:
        """
        Insert a scheduled tweet

        Args:
            tweet_data: Dictionary containing:
                - tweet_text: str
                - source_url: str
                - source_post_id: int
                - scheduled_time: datetime
                - metricool_id: str (optional)
                - status: str (default: 'pending')

        Returns:
            Tweet ID if inserted, None on error
        """
        try:
            self.cursor.execute("""
                INSERT INTO scheduled_tweets (
                    tweet_text, source_url, source_post_id,
                    scheduled_time, metricool_id, status
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tweet_data['tweet_text'],
                tweet_data.get('source_url', ''),
                tweet_data.get('source_post_id'),
                tweet_data['scheduled_time'],
                tweet_data.get('metricool_id', ''),
                tweet_data.get('status', 'pending')
            ))

            self.connection.commit()
            tweet_id = self.cursor.lastrowid
            logger.debug(f"Inserted tweet {tweet_id}: {tweet_data['tweet_text'][:50]}...")
            return tweet_id

        except sqlite3.Error as e:
            logger.error(f"Error inserting tweet: {e}")
            return None

    def update_tweet_status(self, tweet_id: int, status: str, metricool_id: str = None):
        """Update tweet status after scheduling/posting"""
        try:
            if metricool_id:
                self.cursor.execute("""
                    UPDATE scheduled_tweets
                    SET status = ?, metricool_id = ?
                    WHERE id = ?
                """, (status, metricool_id, tweet_id))
            else:
                self.cursor.execute("""
                    UPDATE scheduled_tweets
                    SET status = ?
                    WHERE id = ?
                """, (status, tweet_id))

            self.connection.commit()
            logger.debug(f"Updated tweet {tweet_id} status to {status}")

        except sqlite3.Error as e:
            logger.error(f"Error updating tweet status: {e}")

    def get_recent_tweets(self, hours: int = 24) -> List[Dict]:
        """Get tweets scheduled in the last N hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            self.cursor.execute("""
                SELECT * FROM scheduled_tweets
                WHERE created_at >= ?
                ORDER BY scheduled_time DESC
            """, (cutoff_time,))

            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error getting recent tweets: {e}")
            return []

    def cleanup_old_posts(self, days: int = 30):
        """Delete posts older than N days to keep database clean"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            self.cursor.execute("""
                DELETE FROM scraped_posts
                WHERE scraped_at < ?
            """, (cutoff_date,))

            deleted_count = self.cursor.rowcount
            self.connection.commit()
            logger.info(f"Cleaned up {deleted_count} old posts")

        except sqlite3.Error as e:
            logger.error(f"Error cleaning up old posts: {e}")

    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            stats = {}

            # Total posts
            self.cursor.execute("SELECT COUNT(*) FROM scraped_posts")
            stats['total_posts'] = self.cursor.fetchone()[0]

            # Posts by source
            self.cursor.execute("""
                SELECT source, COUNT(*) as count
                FROM scraped_posts
                GROUP BY source
            """)
            stats['posts_by_source'] = dict(self.cursor.fetchall())

            # Total tweets
            self.cursor.execute("SELECT COUNT(*) FROM scheduled_tweets")
            stats['total_tweets'] = self.cursor.fetchone()[0]

            # Tweets by status
            self.cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM scheduled_tweets
                GROUP BY status
            """)
            stats['tweets_by_status'] = dict(self.cursor.fetchall())

            # Average relevance score
            self.cursor.execute("SELECT AVG(relevance_score) FROM scraped_posts")
            stats['avg_relevance'] = round(self.cursor.fetchone()[0] or 0, 2)

            return stats

        except sqlite3.Error as e:
            logger.error(f"Error getting stats: {e}")
            return {}

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.debug("Database connection closed")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


if __name__ == "__main__":
    # Test database creation
    logging.basicConfig(level=logging.INFO)

    db = NewsDatabase("test_ai_news.db")
    print("Database created successfully!")
    print("Stats:", db.get_stats())
    db.close()

    # Clean up test database
    if os.path.exists("test_ai_news.db"):
        os.remove("test_ai_news.db")
        print("Test database removed")
