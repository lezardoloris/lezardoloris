"""
Metricool API Integration
Schedule tweets via Metricool's scheduling API
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import time
from config import METRICOOL_CONFIG, RATE_LIMITS

logger = logging.getLogger(__name__)


class MetricoolAPI:
    """Metricool API client for scheduling social media posts"""

    def __init__(self):
        self.token = METRICOOL_CONFIG['token']
        self.user_id = METRICOOL_CONFIG['user_id']
        self.blog_id = METRICOOL_CONFIG['blog_id']
        self.base_url = "https://api.metricool.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        })

    def test_connection(self) -> bool:
        """
        Test Metricool API connection

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to get user info
            response = self.session.get(
                f"{self.base_url}/user",
                timeout=10
            )

            if response.status_code == 200:
                logger.info("✅ Metricool API connection successful")
                return True
            else:
                logger.error(f"❌ Metricool API connection failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Metricool API connection error: {e}")
            return False

    def schedule_tweet(
        self,
        text: str,
        scheduled_time: datetime,
        media_urls: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Schedule a tweet via Metricool

        Args:
            text: Tweet text content
            scheduled_time: When to post the tweet
            media_urls: Optional list of media URLs to attach

        Returns:
            Metricool post ID if successful, None otherwise
        """
        try:
            # Prepare post data
            post_data = {
                'userId': self.user_id,
                'blogId': self.blog_id,
                'text': text,
                'scheduledTime': scheduled_time.isoformat(),
                'platform': 'twitter',
                'status': 'scheduled',
            }

            # Add media if provided
            if media_urls:
                post_data['media'] = [
                    {'url': url, 'type': 'image'} for url in media_urls
                ]

            # Make API request
            response = self.session.post(
                f"{self.base_url}/posts",
                json=post_data,
                timeout=15
            )

            if response.status_code in [200, 201]:
                result = response.json()
                post_id = result.get('id', result.get('postId', ''))
                logger.info(f"✅ Tweet scheduled successfully: {post_id}")
                logger.debug(f"Tweet: {text[:50]}... at {scheduled_time}")
                return post_id

            else:
                logger.error(f"❌ Failed to schedule tweet: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error scheduling tweet: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error scheduling tweet: {e}")
            return None

    def schedule_multiple_tweets(
        self,
        tweets: List[Dict],
        start_time: datetime,
        interval_hours: int = 4
    ) -> Dict[str, int]:
        """
        Schedule multiple tweets with automatic time spacing

        Args:
            tweets: List of tweet dictionaries with 'text' and optional 'media_urls'
            start_time: Time to schedule first tweet
            interval_hours: Hours between tweets

        Returns:
            Dictionary with counts: {'success': N, 'failed': M}
        """
        results = {'success': 0, 'failed': 0}
        current_time = start_time

        for i, tweet in enumerate(tweets):
            # Schedule the tweet
            post_id = self.schedule_tweet(
                text=tweet['text'],
                scheduled_time=current_time,
                media_urls=tweet.get('media_urls')
            )

            if post_id:
                results['success'] += 1
            else:
                results['failed'] += 1

            # Move to next time slot
            current_time += timedelta(hours=interval_hours)

            # Rate limiting
            if i < len(tweets) - 1:  # Don't delay after last tweet
                delay = RATE_LIMITS['metricool']['delay_between_posts']
                time.sleep(delay)

        logger.info(f"Batch scheduling complete: {results['success']} success, {results['failed']} failed")
        return results

    def get_scheduled_posts(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get scheduled posts from Metricool

        Args:
            start_date: Start of date range (default: today)
            end_date: End of date range (default: 7 days from now)

        Returns:
            List of scheduled post dictionaries
        """
        try:
            # Default date range
            if not start_date:
                start_date = datetime.now()
            if not end_date:
                end_date = datetime.now() + timedelta(days=7)

            params = {
                'userId': self.user_id,
                'blogId': self.blog_id,
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat(),
                'status': 'scheduled',
            }

            response = self.session.get(
                f"{self.base_url}/posts",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                posts = response.json()
                logger.info(f"Retrieved {len(posts)} scheduled posts")
                return posts
            else:
                logger.error(f"Failed to get scheduled posts: {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting scheduled posts: {e}")
            return []

    def delete_post(self, post_id: str) -> bool:
        """
        Delete a scheduled post

        Args:
            post_id: Metricool post ID

        Returns:
            True if deleted, False otherwise
        """
        try:
            response = self.session.delete(
                f"{self.base_url}/posts/{post_id}",
                params={
                    'userId': self.user_id,
                    'blogId': self.blog_id,
                },
                timeout=10
            )

            if response.status_code in [200, 204]:
                logger.info(f"✅ Post {post_id} deleted")
                return True
            else:
                logger.error(f"❌ Failed to delete post: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error deleting post: {e}")
            return False

    def update_post(
        self,
        post_id: str,
        text: Optional[str] = None,
        scheduled_time: Optional[datetime] = None
    ) -> bool:
        """
        Update a scheduled post

        Args:
            post_id: Metricool post ID
            text: New text content (optional)
            scheduled_time: New scheduled time (optional)

        Returns:
            True if updated, False otherwise
        """
        try:
            update_data = {
                'userId': self.user_id,
                'blogId': self.blog_id,
            }

            if text:
                update_data['text'] = text
            if scheduled_time:
                update_data['scheduledTime'] = scheduled_time.isoformat()

            response = self.session.put(
                f"{self.base_url}/posts/{post_id}",
                json=update_data,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"✅ Post {post_id} updated")
                return True
            else:
                logger.error(f"❌ Failed to update post: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error updating post: {e}")
            return False

    def get_post_analytics(self, post_id: str) -> Optional[Dict]:
        """
        Get analytics for a posted tweet

        Args:
            post_id: Metricool post ID

        Returns:
            Analytics dictionary or None
        """
        try:
            response = self.session.get(
                f"{self.base_url}/posts/{post_id}/analytics",
                params={
                    'userId': self.user_id,
                    'blogId': self.blog_id,
                },
                timeout=10
            )

            if response.status_code == 200:
                analytics = response.json()
                logger.debug(f"Retrieved analytics for post {post_id}")
                return analytics
            else:
                logger.warning(f"Analytics not available for post {post_id}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting post analytics: {e}")
            return None


class MetricoolScheduler:
    """High-level scheduler for managing tweet posting schedule"""

    def __init__(self, api: Optional[MetricoolAPI] = None):
        self.api = api or MetricoolAPI()

    def calculate_next_post_times(
        self,
        num_posts: int,
        target_hours: List[int],
        timezone_name: str = 'America/New_York'
    ) -> List[datetime]:
        """
        Calculate optimal posting times based on target hours

        Args:
            num_posts: Number of posts to schedule
            target_hours: Preferred hours (24-hour format)
            timezone_name: Timezone for scheduling

        Returns:
            List of datetime objects for scheduling
        """
        from pytz import timezone
        import pytz

        tz = timezone(timezone_name)
        now = datetime.now(tz)

        post_times = []
        current_day = now.date()

        for i in range(num_posts):
            # Cycle through target hours
            target_hour = target_hours[i % len(target_hours)]

            # Create datetime for target hour
            post_time = tz.localize(
                datetime.combine(current_day, datetime.min.time()).replace(hour=target_hour)
            )

            # If time has passed today, schedule for next occurrence
            if post_time <= now:
                # Move to next day for this hour
                days_ahead = 1 + (i // len(target_hours))
                post_time = post_time + timedelta(days=days_ahead)

            post_times.append(post_time)

            # Move to next slot
            if (i + 1) % len(target_hours) == 0:
                current_day += timedelta(days=1)

        return post_times

    def schedule_tweets_optimally(
        self,
        tweets: List[Dict],
        target_hours: List[int],
        timezone_name: str = 'America/New_York'
    ) -> Dict[str, int]:
        """
        Schedule tweets at optimal times

        Args:
            tweets: List of tweet dictionaries
            target_hours: Preferred posting hours
            timezone_name: Timezone for scheduling

        Returns:
            Results dictionary with success/failed counts
        """
        post_times = self.calculate_next_post_times(
            num_posts=len(tweets),
            target_hours=target_hours,
            timezone_name=timezone_name
        )

        results = {'success': 0, 'failed': 0, 'scheduled_times': []}

        for tweet, post_time in zip(tweets, post_times):
            post_id = self.api.schedule_tweet(
                text=tweet['text'],
                scheduled_time=post_time,
                media_urls=tweet.get('media_urls')
            )

            if post_id:
                results['success'] += 1
                results['scheduled_times'].append(post_time)
            else:
                results['failed'] += 1

            # Rate limiting
            time.sleep(RATE_LIMITS['metricool']['delay_between_posts'])

        return results


if __name__ == "__main__":
    # Test Metricool API connection
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    api = MetricoolAPI()

    print("\n" + "=" * 50)
    print("METRICOOL API CONNECTION TEST")
    print("=" * 50 + "\n")

    if api.test_connection():
        print("✅ Connection successful!")
        print("\nYou can now use the Metricool API to schedule tweets.")
    else:
        print("❌ Connection failed!")
        print("\nPlease check your .env file:")
        print("  - METRICOOL_TOKEN")
        print("  - METRICOOL_USER_ID")
        print("  - METRICOOL_BLOG_ID")
        sys.exit(1)
