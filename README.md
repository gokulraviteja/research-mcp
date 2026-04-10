# Research MCP Server

An extensible Model Context Protocol (MCP) server that provides access to multiple research sources (Twitter, Reddit, etc.) with unified interface for AI assistants. Built for research and analysis purposes.

## Features

### Current Sources
- **Twitter/X** - 6 core tools for timeline, search, and tweet retrieval

### Architecture
- **Modular design** - Sources are separate modules for easy addition of new platforms
- **Cookie-based auth** - Twitter uses cookie authentication (no API keys needed)
- **Client caching** - Efficient reuse of authenticated sessions
- **Extensible** - Tool naming convention allows seamless addition of new sources

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd research-mcp
```

2. Create and activate a Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Copy environment template:
```bash
cp env_example.txt .env
# Edit .env with your Twitter cookies if needed
```

## Getting Twitter Cookies

Twitter authentication uses cookies, not API keys:

1. Open [twitter.com](https://twitter.com) or [x.com](https://x.com) in your browser
2. Log in to your account
3. Open Developer Tools (F12)
4. Navigate to: **Application/Storage → Cookies → twitter.com** (or x.com)
5. Find and copy these cookies:
   - `ct0` - CSRF token
   - `auth_token` - Session token

Both are required for all Twitter tools.

## Quick Start - Testing

Before using the server, test your setup with:

```bash
# Quick manual test (recommended first step)
python test_manual.py
```

Or with pytest:
```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

See [TESTING.md](TESTING.md) for detailed testing guide.

## Twitter Tools

### 1. twitter_authenticate
Test authentication and get user info.

```json
{
  "tool": "twitter_authenticate",
  "arguments": {
    "ct0": "your_ct0_cookie",
    "auth_token": "your_auth_token"
  }
}
```

**Response:**
```json
{
  "authenticated": true,
  "user": {
    "id": "123456789",
    "username": "example_user",
    "name": "Example User",
    "followers_count": 1000,
    "following_count": 500,
    "tweet_count": 5000,
    "verified": true
  }
}
```

### 2. twitter_get_timeline
Get tweets from your timeline.

```json
{
  "tool": "twitter_get_timeline",
  "arguments": {
    "count": 20,
    "ct0": "your_ct0_cookie",
    "auth_token": "your_auth_token"
  }
}
```

**Parameters:**
- `count` (int, optional): Number of tweets (default: 20, max: 100)

### 3. twitter_get_latest_timeline
Get latest tweets from your timeline.

```json
{
  "tool": "twitter_get_latest_timeline",
  "arguments": {
    "count": 20,
    "ct0": "your_ct0_cookie",
    "auth_token": "your_auth_token"
  }
}
```

### 4. twitter_search_tweets
Search for tweets with a query.

```json
{
  "tool": "twitter_search_tweets",
  "arguments": {
    "query": "artificial intelligence",
    "count": 20,
    "product": "Latest",
    "ct0": "your_ct0_cookie",
    "auth_token": "your_auth_token"
  }
}
```

**Parameters:**
- `query` (string, required): Search query
- `count` (int, optional): Number of tweets (default: 20, max: 100)
- `product` (string, optional): "Top" or "Latest" (default: "Latest")

### 5. twitter_get_tweet
Get a specific tweet by ID.

```json
{
  "tool": "twitter_get_tweet",
  "arguments": {
    "tweet_id": "1234567890123456789",
    "ct0": "your_ct0_cookie",
    "auth_token": "your_auth_token"
  }
}
```

### 6. twitter_get_tweet_replies
Get replies to a specific tweet.

```json
{
  "tool": "twitter_get_tweet_replies",
  "arguments": {
    "tweet_id": "1234567890123456789",
    "count": 20,
    "ct0": "your_ct0_cookie",
    "auth_token": "your_auth_token"
  }
}
```

**Response:**
```json
{
  "original_tweet": {
    "id": "1234567890123456789",
    "text": "Original tweet text",
    "author": "author_username",
    "author_name": "Author Name",
    "created_at": "2024-03-28T10:30:00",
    "like_count": 100,
    "retweet_count": 50,
    "reply_count": 25
  },
  "replies": [
    {
      "id": "1234567890123456790",
      "text": "Reply text",
      "author": "reply_author",
      "author_name": "Reply Author",
      "created_at": "2024-03-28T10:35:00",
      "like_count": 5,
      "retweet_count": 0,
      "reply_count": 0
    }
  ],
  "total_replies_retrieved": 1
}
```

## Running the Server

```bash
python server.py
```

The server listens on stdio and will wait for MCP client connections.

## Adding New Sources (Reddit, Hacker News, etc.)

The architecture is designed for easy extension:

1. Create a new module in `sources/`:
```bash
touch sources/reddit.py
```

2. Implement your source class:
```python
class RedditSource:
    def __init__(self):
        # Initialize with caching, auth, etc.
        pass

    async def search(self, query: str, count: int = 20) -> List[Dict[str, Any]]:
        # Implementation
        pass
```

3. Add to `sources/__init__.py`:
```python
from .reddit import RedditSource
__all__ = ["TwitterSource", "RedditSource"]
```

4. Import in `server.py`:
```python
from sources import TwitterSource, RedditSource
self.reddit = RedditSource()
```

5. Add tools to `handle_list_tools()` with `reddit_` prefix

6. Handle in `_handle_reddit_tool()` method

The naming convention `{source}_{operation}` keeps tools organized and discoverable.

## Architecture Overview

```
research-mcp/
├── server.py              # Main MCP server, dispatches tools
├── sources/               # Data source implementations
│   ├── __init__.py
│   └── twitter.py         # Twitter source (6 tools)
├── requirements.txt       # Python dependencies
├── mcp_config.json        # MCP server configuration
├── env_example.txt        # Environment variables template
└── README.md             # This file
```

### Design Decisions

1. **Modular Sources** - Each platform is a separate module, easy to maintain and extend
2. **Tool Naming** - `{source}_{operation}` format allows clear namespace separation
3. **Client Caching** - Authenticated clients are cached by credentials to avoid re-authentication
4. **Async/Await** - All operations are async-friendly for MCP integration
5. **Credential Handling** - Cookies/credentials passed per-tool for flexibility

## Security Notes

- **Never commit credentials** - Always use `.env` and `.gitignore`
- **Cookie-based auth** - Twitter cookies are temporary; regenerate if expired
- **No API keys stored** - Credentials are passed at call time
- **Environment variables** - Use env files for local testing only

## Twikit Patches

This project includes runtime patches for `twikit 2.3.3` to handle recent Twitter/X changes:

1. **Webpack chunk format** — Twitter changed their JS bundling from `'ondemand.s': 'HASH'` to a webpack chunk ID mapping. Patched in `sources/twitter.py` via monkey-patch on `ClientTransaction.get_indices`.
2. **CSRF token refresh** — After fetching x.com during transaction init, Twitter issues a fresh `ct0` cookie. Twikit was discarding it, causing CSRF mismatches. Patched in `twikit/client/client.py`.
3. **Tweet reply cursor parsing** — Twitter changed the response structure for `get_tweet_by_id`. Patched in `twikit/client/client.py`.

> **Note:** Patches 2 and 3 are applied directly to the vendored twikit package. If you reinstall twikit, you'll need to reapply them. Patch 1 is applied automatically at import time.

## Troubleshooting

### Authentication Fails
- Check cookies are not expired (reload twitter.com and re-copy)
- Ensure both `ct0` and `auth_token` are provided
- Try `twitter_authenticate` tool first to test credentials

### No Results from Search
- Verify Twitter cookies are current
- Try simpler search queries
- Check Twitter API/site status (twikit depends on unofficial API)

### Client Caching Issues
- Each unique `ct0` value creates a new cached client
- If changing accounts, use different `ct0` values

## License

See LICENSE file for details.

## Disclaimer

This project uses `twikit` for Twitter API access, which is an unofficial library. Twitter/X may change their API or terms of service. Use at your own risk.
