#!/usr/bin/env python3
"""
Manual test script for research-mcp

Simple script to test TwitterSource without pytest.
Run with: python test_manual.py

Setup:
1. Copy env_example.txt to .env
2. Add your Twitter cookies to .env:
   TWITTER_CT0=your_ct0_cookie
   TWITTER_AUTH_TOKEN=your_auth_token
3. Run: python test_manual.py
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv
from sources.twitter import TwitterSource

# Load environment variables from .env file
load_dotenv()

# Get cookies from environment variables
CT0 = os.getenv("TWITTER_CT0")
AUTH_TOKEN = os.getenv("TWITTER_AUTH_TOKEN")


async def print_section(title):
    """Print a test section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


async def test_authenticate():
    """Test 1: Authentication"""
    await print_section("TEST 1: Authentication")

    try:
        result = await twitter.authenticate(CT0, AUTH_TOKEN)
        if result.get("authenticated"):
            user = result["user"]
            print(f"✓ Authentication successful!")
            print(f"  Username: {user['username']}")
            print(f"  Name: {user['name']}")
            print(f"  Followers: {user['followers_count']:,}")
            print(f"  Verified: {user['verified']}")
            return True
        else:
            print("✗ Authentication failed")
            return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_get_timeline():
    """Test 2: Get Timeline"""
    await print_section("TEST 2: Get Timeline")

    try:
        tweets = await twitter.get_timeline(CT0, AUTH_TOKEN, count=3)
        print(f"✓ Retrieved {len(tweets)} timeline tweets\n")
        for i, tweet in enumerate(tweets[:3], 1):
            print(f"  Tweet {i}:")
            print(f"    Author: @{tweet['author']}")
            print(f"    Text: {tweet['text'][:80]}...")
            print(f"    Likes: {tweet['like_count']}, Replies: {tweet['reply_count']}")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_get_latest_timeline():
    """Test 3: Get Latest Timeline"""
    await print_section("TEST 3: Get Latest Timeline")

    try:
        tweets = await twitter.get_latest_timeline(CT0, AUTH_TOKEN, count=3)
        print(f"✓ Retrieved {len(tweets)} latest timeline tweets\n")
        for i, tweet in enumerate(tweets[:2], 1):
            print(f"  Tweet {i}: @{tweet['author']} - {tweet['text'][:60]}...")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_search_tweets():
    """Test 4: Search Tweets"""
    await print_section("TEST 4: Search Tweets")

    try:
        # Test with Latest product
        tweets = await twitter.search_tweets(
            CT0, AUTH_TOKEN,
            query="python artificial intelligence",
            count=3,
            product="Latest"
        )
        print(f"✓ Search successful! Found {len(tweets)} results\n")
        for i, tweet in enumerate(tweets[:3], 1):
            print(f"  Result {i}:")
            print(f"    Author: @{tweet['author']}")
            print(f"    Text: {tweet['text'][:70]}...")
            print(f"    Likes: {tweet['like_count']}")
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_get_tweet():
    """Test 5: Get Single Tweet"""
    await print_section("TEST 5: Get Single Tweet by ID")

    try:
        # First search to get a tweet ID
        tweets = await twitter.search_tweets(
            CT0, AUTH_TOKEN,
            query="research",
            count=1
        )

        if tweets:
            tweet_id = tweets[0]["id"]
            tweet = await twitter.get_tweet(CT0, AUTH_TOKEN, tweet_id)

            if "error" not in tweet:
                print(f"✓ Retrieved tweet {tweet_id}\n")
                print(f"  Author: @{tweet['author']}")
                print(f"  Name: {tweet['author_name']}")
                print(f"  Text: {tweet['text'][:100]}...")
                print(f"  Created: {tweet['created_at']}")
                print(f"  Engagement: ❤️ {tweet['like_count']} | 🔄 {tweet['retweet_count']} | 💬 {tweet['reply_count']}")
                return True
            else:
                print(f"✗ Tweet not found")
                return False
        else:
            print("✗ No tweets found to test")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_get_tweet_replies():
    """Test 6: Get Tweet Replies"""
    await print_section("TEST 6: Get Tweet Replies")

    try:
        # Get a tweet that likely has replies
        tweets = await twitter.search_tweets(
            CT0, AUTH_TOKEN,
            query="twitter",
            count=1
        )

        if tweets:
            tweet_id = tweets[0]["id"]
            result = await twitter.get_tweet_replies(
                CT0, AUTH_TOKEN,
                tweet_id,
                count=3
            )

            original = result["original_tweet"]
            replies = result["replies"]

            print(f"✓ Retrieved replies to tweet {tweet_id}\n")
            print(f"  Original Tweet:")
            print(f"    @{original['author']}: {original['text'][:70]}...")
            print(f"    Replies: {original['reply_count']}\n")

            if replies:
                print(f"  {len(replies)} Replies:")
                for i, reply in enumerate(replies[:2], 1):
                    print(f"    Reply {i}: @{reply['author']} - {reply['text'][:60]}...")
            else:
                print("  (No replies loaded)")

            return True
        else:
            print("✗ No tweets found")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def test_client_caching():
    """Test 7: Client Caching"""
    await print_section("TEST 7: Client Caching")

    try:
        # First call
        await twitter.authenticate(CT0, AUTH_TOKEN)
        cached_clients_1 = len(twitter.authenticated_clients)

        # Second call with same cookies
        await twitter.authenticate(CT0, AUTH_TOKEN)
        cached_clients_2 = len(twitter.authenticated_clients)

        if cached_clients_1 == cached_clients_2 == 1:
            print(f"✓ Client caching works!")
            print(f"  Same client reused (cache size: {cached_clients_2})")
            return True
        else:
            print(f"✗ Caching issue (cache sizes: {cached_clients_1}, {cached_clients_2})")
            return False

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  Research MCP - Twitter Source Tests")
    print("="*60)

    # Check if cookies are set from environment
    if not CT0 or not AUTH_TOKEN:
        print("\n⚠️  ERROR: Twitter cookies not found in .env file")
        print("\nSetup instructions:")
        print("  1. Copy env_example.txt to .env:")
        print("     cp env_example.txt .env")
        print("\n  2. Edit .env and add your Twitter cookies:")
        print("     TWITTER_CT0=your_ct0_value")
        print("     TWITTER_AUTH_TOKEN=your_auth_token_value")
        print("\n  3. How to get cookies:")
        print("     - Go to twitter.com and log in")
        print("     - Open DevTools (F12)")
        print("     - Application → Storage → Cookies → twitter.com")
        print("     - Copy ct0 and auth_token values")
        print("\n  4. Run tests again:")
        print("     python test_manual.py")
        return

    # Shared TwitterSource instance (avoids repeated auth/init)
    global twitter
    twitter = TwitterSource()

    # Run tests
    results = []
    results.append(("Authentication", await test_authenticate()))
    results.append(("Get Timeline", await test_get_timeline()))
    results.append(("Get Latest Timeline", await test_get_latest_timeline()))
    results.append(("Search Tweets", await test_search_tweets()))
    results.append(("Get Single Tweet", await test_get_tweet()))
    results.append(("Get Tweet Replies", await test_get_tweet_replies()))
    results.append(("Client Caching", await test_client_caching()))

    # Summary
    await print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:8} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Server is ready to use.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
