"""
Unit tests for TwitterSource

Test the core Twitter functionality without MCP overhead.
Run with: pytest tests/test_twitter_source.py -v

Setup:
1. Copy env_example.txt to .env
2. Add your Twitter cookies to .env:
   TWITTER_CT0=your_ct0_cookie
   TWITTER_AUTH_TOKEN=your_auth_token
3. Run: pytest tests/ -v
"""

import asyncio
import os
import pytest
from dotenv import load_dotenv
from sources.twitter import TwitterSource

# Load environment variables from .env file
load_dotenv()


class TestTwitterSourceUnit:
    """Unit tests for TwitterSource using real Twitter API"""

    @pytest.fixture
    def twitter_source(self):
        """Initialize TwitterSource for each test"""
        return TwitterSource()

    @pytest.fixture
    def valid_cookies(self):
        """
        Twitter cookies for testing loaded from environment variables.

        Setup:
        1. Copy env_example.txt to .env
        2. Add to .env:
           TWITTER_CT0=your_ct0_cookie
           TWITTER_AUTH_TOKEN=your_auth_token
        3. Run: pytest tests/ -v
        """
        ct0 = os.getenv("TWITTER_CT0")
        auth_token = os.getenv("TWITTER_AUTH_TOKEN")

        if not ct0 or not auth_token:
            pytest.skip("Twitter cookies not found in .env file. See test_twitter_source.py for setup instructions.")

        return {
            "ct0": ct0,
            "auth_token": auth_token
        }

    @pytest.mark.asyncio
    async def test_authenticate_valid_cookies(self, twitter_source, valid_cookies):
        """Test authentication with valid cookies"""
        result = await twitter_source.authenticate(
            valid_cookies["ct0"],
            valid_cookies["auth_token"]
        )

        # Verify response structure
        assert "authenticated" in result
        assert result["authenticated"] is True
        assert "user" in result

        user = result["user"]
        assert "id" in user
        assert "username" in user
        assert "name" in user
        assert "followers_count" in user
        assert isinstance(user["followers_count"], int)

    @pytest.mark.asyncio
    async def test_authenticate_invalid_cookies(self, twitter_source):
        """Test authentication with invalid cookies (should fail gracefully)"""
        with pytest.raises(ValueError, match="Authentication failed"):
            await twitter_source.authenticate(
                "invalid_ct0",
                "invalid_auth_token"
            )

    @pytest.mark.asyncio
    async def test_get_timeline(self, twitter_source, valid_cookies):
        """Test getting timeline tweets"""
        result = await twitter_source.get_timeline(
            valid_cookies["ct0"],
            valid_cookies["auth_token"],
            count=5
        )

        # Should return a list
        assert isinstance(result, list)
        assert len(result) > 0

        # Check tweet structure
        tweet = result[0]
        assert "id" in tweet
        assert "text" in tweet
        assert "author" in tweet
        assert "created_at" in tweet
        assert "like_count" in tweet
        assert "retweet_count" in tweet
        assert "reply_count" in tweet

    @pytest.mark.asyncio
    async def test_get_latest_timeline(self, twitter_source, valid_cookies):
        """Test getting latest timeline tweets"""
        result = await twitter_source.get_latest_timeline(
            valid_cookies["ct0"],
            valid_cookies["auth_token"],
            count=5
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # Verify tweet structure
        tweet = result[0]
        assert "id" in tweet
        assert "text" in tweet

    @pytest.mark.asyncio
    async def test_search_tweets_latest(self, twitter_source, valid_cookies):
        """Test searching tweets with Latest product"""
        result = await twitter_source.search_tweets(
            valid_cookies["ct0"],
            valid_cookies["auth_token"],
            query="python",
            count=5,
            product="Latest"
        )

        assert isinstance(result, list)
        assert len(result) > 0

        # All results should match search query (loosely)
        tweet = result[0]
        assert "id" in tweet
        assert "text" in tweet

    @pytest.mark.asyncio
    async def test_search_tweets_top(self, twitter_source, valid_cookies):
        """Test searching tweets with Top product"""
        result = await twitter_source.search_tweets(
            valid_cookies["ct0"],
            valid_cookies["auth_token"],
            query="python",
            count=5,
            product="Top"
        )

        assert isinstance(result, list)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_search_tweets_invalid_product(self, twitter_source, valid_cookies):
        """Test that invalid product defaults to Latest"""
        result = await twitter_source.search_tweets(
            valid_cookies["ct0"],
            valid_cookies["auth_token"],
            query="python",
            count=5,
            product="InvalidProduct"  # Should default to "Latest"
        )

        # Should still work, using default product
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_tweet(self, twitter_source, valid_cookies):
        """Test getting a specific tweet by ID"""
        # First, get a tweet ID from search
        tweets = await twitter_source.search_tweets(
            valid_cookies["ct0"],
            valid_cookies["auth_token"],
            query="python",
            count=1
        )

        if tweets:
            tweet_id = tweets[0]["id"]
            result = await twitter_source.get_tweet(
                valid_cookies["ct0"],
                valid_cookies["auth_token"],
                tweet_id
            )

            assert "id" in result
            assert result["id"] == tweet_id
            assert "text" in result
            assert "author" in result

    @pytest.mark.asyncio
    async def test_get_tweet_not_found(self, twitter_source, valid_cookies):
        """Test getting a non-existent tweet"""
        result = await twitter_source.get_tweet(
            valid_cookies["ct0"],
            valid_cookies["auth_token"],
            "999999999999999999"
        )

        # Should return error dict
        assert "error" in result or "id" in result  # Either error or empty result

    @pytest.mark.asyncio
    async def test_get_tweet_replies(self, twitter_source, valid_cookies):
        """Test getting replies to a tweet"""
        # First, get a tweet that likely has replies
        tweets = await twitter_source.search_tweets(
            valid_cookies["ct0"],
            valid_cookies["auth_token"],
            query="python",
            count=1
        )

        if tweets:
            tweet_id = tweets[0]["id"]
            result = await twitter_source.get_tweet_replies(
                valid_cookies["ct0"],
                valid_cookies["auth_token"],
                tweet_id,
                count=5
            )

            assert "original_tweet" in result
            assert "replies" in result
            assert "total_replies_retrieved" in result

            original = result["original_tweet"]
            assert "id" in original
            assert original["id"] == tweet_id

            # Replies should be a list
            assert isinstance(result["replies"], list)

    @pytest.mark.asyncio
    async def test_client_caching(self, twitter_source, valid_cookies):
        """Test that authenticated clients are cached"""
        ct0 = valid_cookies["ct0"]
        auth_token = valid_cookies["auth_token"]

        # First call creates client
        await twitter_source.authenticate(ct0, auth_token)
        assert ct0 in twitter_source.authenticated_clients

        # Second call uses cached client
        cached_client = twitter_source.authenticated_clients[ct0]
        await twitter_source.authenticate(ct0, auth_token)
        assert twitter_source.authenticated_clients[ct0] is cached_client


class TestTwitterSourceIntegration:
    """Integration tests that test multiple operations together"""

    @pytest.fixture
    def twitter_source(self):
        return TwitterSource()

    @pytest.fixture
    def valid_cookies(self):
        ct0 = os.getenv("TWITTER_CT0")
        auth_token = os.getenv("TWITTER_AUTH_TOKEN")

        if not ct0 or not auth_token:
            pytest.skip("Twitter cookies not found in .env file")

        return {
            "ct0": ct0,
            "auth_token": auth_token
        }

    @pytest.mark.asyncio
    async def test_workflow_authenticate_and_search(self, twitter_source, valid_cookies):
        """Test complete workflow: authenticate and then search"""
        # Authenticate
        auth_result = await twitter_source.authenticate(
            valid_cookies["ct0"],
            valid_cookies["auth_token"]
        )
        assert auth_result["authenticated"] is True
        username = auth_result["user"]["username"]

        # Search using authenticated session
        search_result = await twitter_source.search_tweets(
            valid_cookies["ct0"],
            valid_cookies["auth_token"],
            query="research",
            count=5
        )

        assert isinstance(search_result, list)
        assert len(search_result) > 0

    @pytest.mark.asyncio
    async def test_workflow_search_and_get_tweet(self, twitter_source, valid_cookies):
        """Test workflow: search for tweet and get its details"""
        # Search
        tweets = await twitter_source.search_tweets(
            valid_cookies["ct0"],
            valid_cookies["auth_token"],
            query="twitter",
            count=5
        )

        if tweets:
            tweet_id = tweets[0]["id"]

            # Get the specific tweet
            tweet = await twitter_source.get_tweet(
                valid_cookies["ct0"],
                valid_cookies["auth_token"],
                tweet_id
            )

            assert tweet["id"] == tweet_id
            assert len(tweet["text"]) > 0
