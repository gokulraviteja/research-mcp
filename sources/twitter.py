"""
Twitter Source Module for Research MCP Server

Provides Twitter API access through twikit library with cookie-based authentication.
Implements 6 core tools for timeline, search, and tweet operations.
"""

import json
import re
from typing import Any, Dict, List, Optional
from twikit import Client
import twikit.x_client_transaction.transaction as _tx
# Monkey-patch 1: Twitter changed their webpack chunk format.
# Old format: 'ondemand.s': 'HASH'
# New format: CHUNK_ID:"ondemand.s" ... CHUNK_ID:"HASH"
_ORIGINAL_GET_INDICES = _tx.ClientTransaction.get_indices

async def _patched_get_indices(self, home_page_response, session, headers):
    try:
        return await _ORIGINAL_GET_INDICES(self, home_page_response, session, headers)
    except Exception:
        pass

    response = self.validate_response(home_page_response) or self.home_page_response
    page_text = str(response)

    chunk_match = re.search(r'(\d+):"ondemand\.s"', page_text)
    if not chunk_match:
        raise Exception("Couldn't find ondemand.s chunk ID")

    chunk_id = chunk_match.group(1)
    hash_match = re.search(chunk_id + r':"([a-f0-9]+)"', page_text)
    if not hash_match:
        raise Exception("Couldn't find hash for ondemand.s chunk")

    file_hash = hash_match.group(1)
    on_demand_file_url = f"https://abs.twimg.com/responsive-web/client-web/ondemand.s.{file_hash}a.js"
    on_demand_response = await session.request(method="GET", url=on_demand_file_url, headers=headers)

    key_byte_indices = []
    for item in _tx.INDICES_REGEX.finditer(str(on_demand_response.text)):
        key_byte_indices.append(item.group(2))

    if not key_byte_indices:
        raise Exception("Couldn't get KEY_BYTE indices from JS file")

    key_byte_indices = list(map(int, key_byte_indices))
    return key_byte_indices[0], key_byte_indices[1:]

_tx.ClientTransaction.get_indices = _patched_get_indices


class TwitterSource:
    """Handle Twitter-specific operations with client caching"""

    def __init__(self):
        """Initialize Twitter source with empty client cache"""
        self.authenticated_clients = {}  # Cache: ct0 -> Client

    async def authenticate(self, ct0: str, auth_token: str) -> Dict[str, Any]:
        """
        Test authentication and return user info

        Args:
            ct0: Twitter CSRF token cookie
            auth_token: Twitter auth token cookie

        Returns:
            Dictionary with user authentication info
        """
        client = await self._get_authenticated_client(ct0, auth_token)
        user = await client.user()

        return {
            "authenticated": True,
            "user": {
                "id": user.id,
                "username": user.screen_name,
                "name": user.name,
                "followers_count": user.followers_count,
                "following_count": user.following_count,
                "tweet_count": user.statuses_count,
                "verified": user.verified
            }
        }

    async def get_timeline(self, ct0: str, auth_token: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        Get tweets from user's timeline

        Args:
            ct0: Twitter CSRF token cookie
            auth_token: Twitter auth token cookie
            count: Number of tweets to retrieve (default: 20, max: 100)

        Returns:
            List of tweet dictionaries
        """
        client = await self._get_authenticated_client(ct0, auth_token)
        tweets = await client.get_timeline(count=count)
        return self._format_tweets(tweets)

    async def get_latest_timeline(self, ct0: str, auth_token: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        Get latest tweets from user's timeline

        Args:
            ct0: Twitter CSRF token cookie
            auth_token: Twitter auth token cookie
            count: Number of tweets to retrieve (default: 20, max: 100)

        Returns:
            List of tweet dictionaries
        """
        client = await self._get_authenticated_client(ct0, auth_token)
        tweets = await client.get_latest_timeline(count=count)
        return self._format_tweets(tweets)

    async def search_tweets(self, ct0: str, auth_token: str, query: str,
                           count: int = 20, product: str = "Latest") -> List[Dict[str, Any]]:
        """
        Search for tweets with query

        Args:
            ct0: Twitter CSRF token cookie
            auth_token: Twitter auth token cookie
            query: Search query string
            count: Number of tweets to retrieve (default: 20, max: 100)
            product: Type of results - "Top" or "Latest" (default: "Latest")

        Returns:
            List of tweet dictionaries
        """
        # Validate product parameter
        if product not in ("Top", "Latest"):
            product = "Latest"

        client = await self._get_authenticated_client(ct0, auth_token)
        tweets = await client.search_tweet(query, product=product, count=count)
        return self._format_tweets(tweets)

    async def get_tweet(self, ct0: str, auth_token: str, tweet_id: str) -> Dict[str, Any]:
        """
        Get a single tweet by ID

        Args:
            ct0: Twitter CSRF token cookie
            auth_token: Twitter auth token cookie
            tweet_id: ID of the tweet to retrieve

        Returns:
            Formatted tweet dictionary
        """
        client = await self._get_authenticated_client(ct0, auth_token)
        tweet = await client.get_tweet_by_id(tweet_id)

        if not tweet:
            return {"error": "Tweet not found"}

        return self._format_tweet(tweet)

    async def get_tweet_replies(self, ct0: str, auth_token: str, tweet_id: str,
                                count: int = 20) -> Dict[str, Any]:
        """
        Get replies to a specific tweet

        Args:
            ct0: Twitter CSRF token cookie
            auth_token: Twitter auth token cookie
            tweet_id: ID of the tweet
            count: Number of replies to retrieve (default: 20, max: 100)

        Returns:
            Dictionary with original tweet and replies
        """
        client = await self._get_authenticated_client(ct0, auth_token)
        tweet = await client.get_tweet_by_id(tweet_id)

        if not tweet:
            return {"error": "Tweet not found"}

        replies_data = []

        # Check if tweet has replies
        if hasattr(tweet, 'replies') and tweet.replies is not None:
            reply_count = 0
            for reply in tweet.replies:
                if reply_count >= count:
                    break
                replies_data.append(self._format_tweet(reply))
                reply_count += 1

        return {
            "original_tweet": self._format_tweet(tweet),
            "replies": replies_data,
            "total_replies_retrieved": len(replies_data)
        }

    async def _get_authenticated_client(self, ct0: str, auth_token: str) -> Client:
        """
        Get or create an authenticated client

        Uses caching to avoid re-authentication for the same cookies.

        Args:
            ct0: Twitter CSRF token cookie
            auth_token: Twitter auth token cookie

        Returns:
            Authenticated Client instance

        Raises:
            ValueError: If authentication fails
        """
        cache_key = ct0

        # Return cached client if available
        if cache_key in self.authenticated_clients:
            return self.authenticated_clients[cache_key]

        # Create and authenticate new client
        client = Client('en-US')
        cookies = {'ct0': ct0, 'auth_token': auth_token}
        client.set_cookies(cookies)

        # Cache the authenticated client
        self.authenticated_clients[cache_key] = client
        return client

    def _format_tweet(self, tweet: Any) -> Dict[str, Any]:
        """
        Format a twikit Tweet object into a dictionary

        Args:
            tweet: twikit Tweet object

        Returns:
            Formatted tweet dictionary
        """
        return {
            "id": tweet.id,
            "text": tweet.text,
            "author": tweet.user.screen_name,
            "author_name": tweet.user.name,
            "author_id": tweet.user.id,
            "created_at": str(tweet.created_at),
            "like_count": tweet.favorite_count,
            "retweet_count": tweet.retweet_count,
            "reply_count": tweet.reply_count
        }

    def _format_tweets(self, tweets: List[Any]) -> List[Dict[str, Any]]:
        """
        Format a list of twikit Tweet objects

        Args:
            tweets: List of twikit Tweet objects

        Returns:
            List of formatted tweet dictionaries
        """
        return [self._format_tweet(tweet) for tweet in tweets]
