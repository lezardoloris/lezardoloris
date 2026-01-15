"""
Tweet Generator for AI News
Generates engaging tweets from filtered content
"""

import logging
import random
import re
from typing import List, Dict, Optional
from config import TWEET_CONFIG

logger = logging.getLogger(__name__)


class TweetGenerator:
    """Generate tweets from AI news posts"""

    def __init__(self):
        self.max_length = TWEET_CONFIG['max_length']
        self.include_hashtags = TWEET_CONFIG['include_hashtags']
        self.hashtags = TWEET_CONFIG['hashtags']
        self.include_url = TWEET_CONFIG['include_url']
        self.emojis_enabled = TWEET_CONFIG['emojis_enabled']
        self.emoji_map = TWEET_CONFIG['emoji_map']
        self.templates = TWEET_CONFIG['templates']

        logger.info("Tweet generator initialized")

    def generate_tweet(self, post: Dict) -> Optional[str]:
        """
        Generate a tweet from a post

        Args:
            post: Post dictionary with title, content, url, etc.

        Returns:
            Generated tweet text or None if generation fails
        """
        try:
            # Extract components
            headline = self._create_headline(post)
            summary = self._create_summary(post)
            url = post.get('url', '')
            emoji = self._select_emoji(post)
            hashtags = self._select_hashtags(post)

            # Choose random template
            template = random.choice(self.templates)

            # Build tweet
            tweet = template.format(
                emoji=emoji if self.emojis_enabled else '',
                headline=headline,
                summary=summary,
                url=url if self.include_url else '',
                hashtags=hashtags if self.include_hashtags else '',
            )

            # Clean up extra whitespace
            tweet = re.sub(r'\s+', ' ', tweet).strip()
            tweet = re.sub(r'\n\s*\n', '\n\n', tweet)

            # Ensure within character limit
            tweet = self._truncate_to_limit(tweet, url)

            logger.debug(f"Generated tweet ({len(tweet)} chars): {tweet[:50]}...")
            return tweet

        except Exception as e:
            logger.error(f"Error generating tweet: {e}")
            return None

    def _create_headline(self, post: Dict) -> str:
        """Extract or create headline from post"""
        title = post.get('title', '')

        # Clean up title
        headline = title.strip()

        # Remove common prefixes
        prefixes_to_remove = [
            r'^\[.*?\]\s*',  # [Subreddit] prefix
            r'^r/\w+\s*[-:]\s*',  # r/subreddit: prefix
        ]

        for pattern in prefixes_to_remove:
            headline = re.sub(pattern, '', headline, flags=re.IGNORECASE)

        # Limit length for headline
        if len(headline) > 100:
            headline = headline[:97] + '...'

        return headline

    def _create_summary(self, post: Dict) -> str:
        """Create brief summary from post content"""
        content = post.get('content', '')

        if not content:
            return ''

        # Clean content
        summary = content.strip()

        # Remove URLs from summary
        summary = re.sub(r'http\S+', '', summary)

        # Take first sentence or first 120 chars
        sentences = re.split(r'[.!?]\s+', summary)
        if sentences:
            summary = sentences[0]

        # Limit length
        if len(summary) > 120:
            summary = summary[:117] + '...'

        return summary

    def _select_emoji(self, post: Dict) -> str:
        """Select appropriate emoji based on post content"""
        if not self.emojis_enabled:
            return ''

        title_lower = post.get('title', '').lower()
        content_lower = post.get('content', '').lower()
        text = f"{title_lower} {content_lower}"

        # Check for emoji triggers
        for trigger, emoji in self.emoji_map.items():
            if trigger in text:
                return emoji

        # Default emoji
        return '🤖'

    def _select_hashtags(self, post: Dict) -> str:
        """Select relevant hashtags for post"""
        if not self.include_hashtags:
            return ''

        # Start with default hashtags
        selected_tags = self.hashtags[:2]  # Use first 2 default tags

        # Add company-specific hashtag if mentioned
        title_lower = post.get('title', '').lower()
        content_lower = post.get('content', '').lower()
        text = f"{title_lower} {content_lower}"

        company_tags = {
            'openai': '#OpenAI',
            'chatgpt': '#ChatGPT',
            'gpt': '#GPT',
            'anthropic': '#Anthropic',
            'claude': '#Claude',
            'google': '#GoogleAI',
            'gemini': '#Gemini',
            'deepmind': '#DeepMind',
            'meta': '#MetaAI',
            'llama': '#LLaMA',
        }

        for keyword, tag in company_tags.items():
            if keyword in text and tag not in selected_tags:
                selected_tags.append(tag)
                break  # Add only one company tag

        # Limit to 3 tags total
        selected_tags = selected_tags[:3]

        return ' '.join(selected_tags)

    def _truncate_to_limit(self, tweet: str, url: str) -> str:
        """
        Ensure tweet is within character limit

        Args:
            tweet: Full tweet text
            url: URL that should be preserved

        Returns:
            Truncated tweet if necessary
        """
        if len(tweet) <= self.max_length:
            return tweet

        # Twitter counts URLs as 23 characters
        url_length = 23 if url else 0

        # Calculate available space
        available = self.max_length - url_length - 10  # Buffer for hashtags/ellipsis

        # Split tweet into parts
        parts = tweet.split('\n')

        # Try to preserve structure
        truncated_parts = []
        current_length = 0

        for part in parts:
            if current_length + len(part) <= available:
                truncated_parts.append(part)
                current_length += len(part) + 2  # +2 for newline
            else:
                # Add truncated version of this part
                remaining = available - current_length - 3
                if remaining > 20:
                    truncated_parts.append(part[:remaining] + '...')
                break

        truncated = '\n'.join(truncated_parts)

        logger.debug(f"Truncated tweet from {len(tweet)} to {len(truncated)} chars")
        return truncated

    def generate_multiple_tweets(
        self,
        posts: List[Dict],
        max_tweets: int = 3
    ) -> List[Dict]:
        """
        Generate multiple tweets from top posts

        Args:
            posts: List of post dictionaries (should be sorted by relevance)
            max_tweets: Maximum number of tweets to generate

        Returns:
            List of tweet dictionaries with 'text', 'source_url', etc.
        """
        tweets = []

        for post in posts[:max_tweets]:
            tweet_text = self.generate_tweet(post)

            if tweet_text:
                tweet_data = {
                    'text': tweet_text,
                    'source_url': post.get('url', ''),
                    'source_post_id': post.get('id'),
                    'relevance_score': post.get('relevance_score', 0),
                }
                tweets.append(tweet_data)

        logger.info(f"✅ Generated {len(tweets)} tweets from {len(posts)} posts")

        return tweets

    def preview_tweet(self, tweet_text: str) -> str:
        """
        Create a formatted preview of the tweet

        Args:
            tweet_text: Tweet text

        Returns:
            Formatted preview string
        """
        char_count = len(tweet_text)
        char_limit = self.max_length

        preview = f"""
┌{'─' * 60}┐
│ TWEET PREVIEW ({char_count}/{char_limit} chars)
├{'─' * 60}┤
│
│ {tweet_text.replace(chr(10), chr(10) + '│ ')}
│
└{'─' * 60}┘
"""
        return preview

    def batch_preview(self, tweets: List[Dict]) -> str:
        """
        Create preview of multiple tweets

        Args:
            tweets: List of tweet dictionaries

        Returns:
            Formatted preview string
        """
        preview = f"\n{'='*60}\n"
        preview += f"GENERATED {len(tweets)} TWEETS\n"
        preview += f"{'='*60}\n\n"

        for i, tweet in enumerate(tweets, 1):
            text = tweet.get('text', '')
            url = tweet.get('source_url', '')

            preview += f"Tweet {i}:\n"
            preview += f"{'-'*60}\n"
            preview += f"{text}\n"
            preview += f"\nSource: {url}\n"
            preview += f"Length: {len(text)} chars\n"
            preview += f"\n"

        return preview


def validate_tweet(tweet_text: str, max_length: int = 280) -> Dict:
    """
    Validate tweet meets Twitter requirements

    Args:
        tweet_text: Tweet text to validate
        max_length: Maximum allowed length

    Returns:
        Dictionary with validation results
    """
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'length': len(tweet_text),
    }

    # Check length
    if len(tweet_text) > max_length:
        results['valid'] = False
        results['errors'].append(f"Tweet exceeds {max_length} characters ({len(tweet_text)} chars)")

    # Check if empty
    if not tweet_text.strip():
        results['valid'] = False
        results['errors'].append("Tweet is empty")

    # Check for too many hashtags
    hashtag_count = len(re.findall(r'#\w+', tweet_text))
    if hashtag_count > 5:
        results['warnings'].append(f"Tweet has {hashtag_count} hashtags (recommended: 1-3)")

    # Check for repeated characters
    if re.search(r'(.)\1{5,}', tweet_text):
        results['warnings'].append("Tweet contains repeated characters")

    # Check for all caps
    words = tweet_text.split()
    caps_words = [w for w in words if w.isupper() and len(w) > 3]
    if len(caps_words) > 3:
        results['warnings'].append("Tweet has many all-caps words")

    return results


if __name__ == "__main__":
    # Test tweet generator
    logging.basicConfig(level=logging.INFO)

    # Sample post for testing
    test_post = {
        'title': 'OpenAI Announces GPT-5: Revolutionary AI Model with Enhanced Capabilities',
        'content': 'OpenAI has officially announced GPT-5, their latest and most advanced language model. The new model features improved reasoning, longer context windows, and better performance across a wide range of tasks.',
        'url': 'https://openai.com/blog/gpt-5',
        'relevance_score': 0.95,
        'source': 'newsapi',
    }

    generator = TweetGenerator()

    print("\n" + "=" * 60)
    print("TWEET GENERATOR TEST")
    print("=" * 60 + "\n")

    # Generate single tweet
    tweet = generator.generate_tweet(test_post)

    if tweet:
        print(generator.preview_tweet(tweet))

        # Validate
        validation = validate_tweet(tweet)
        print(f"\nValidation: {'✅ PASS' if validation['valid'] else '❌ FAIL'}")
        if validation['errors']:
            print("Errors:")
            for error in validation['errors']:
                print(f"  - {error}")
        if validation['warnings']:
            print("Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")

    # Test multiple tweets
    test_posts = [test_post] * 3
    tweets = generator.generate_multiple_tweets(test_posts, max_tweets=3)

    print("\n" + generator.batch_preview(tweets))
