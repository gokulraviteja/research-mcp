# Data Sources Guide

This directory contains implementations for different data sources (Twitter, Reddit, etc.). This guide explains how to add a new source.

## Architecture

Each source is a separate Python module with:
1. A class that handles all operations for that source
2. Methods for each operation (search, fetch, etc.)
3. Consistent response formatting

### Example Structure

```python
class NewSource:
    def __init__(self):
        # Initialize client/session caching
        # Setup any default configuration
        pass

    async def operation_one(self, param1: str, param2: int) -> Dict[str, Any]:
        # Implementation of operation 1
        pass

    async def operation_two(self, param1: str) -> List[Dict[str, Any]]:
        # Implementation of operation 2
        pass
```

## Adding a New Source (Example: Reddit)

### Step 1: Create the Source File

```bash
touch sources/reddit.py
```

### Step 2: Implement the Source Class

```python
"""
Reddit Source Module for Research MCP Server

Provides Reddit API access with user authentication.
"""

from typing import Any, Dict, List, Optional


class RedditSource:
    """Handle Reddit-specific operations"""

    def __init__(self):
        """Initialize Reddit source"""
        self.authenticated_clients = {}  # Cache for authenticated clients

    async def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Test authentication and get user info

        Args:
            username: Reddit username
            password: Reddit password

        Returns:
            Dictionary with authentication info
        """
        # Implementation
        pass

    async def search_subreddit(self, query: str, subreddit: str = "all",
                              count: int = 20) -> List[Dict[str, Any]]:
        """
        Search Reddit posts

        Args:
            query: Search query
            subreddit: Subreddit to search in (default: all)
            count: Number of results (default: 20)

        Returns:
            List of post dictionaries
        """
        # Implementation
        pass

    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Get a specific post by ID

        Args:
            post_id: Reddit post ID

        Returns:
            Post dictionary with comments
        """
        # Implementation
        pass
```

### Step 3: Update sources/__init__.py

```python
from .twitter import TwitterSource
from .reddit import RedditSource

__all__ = ["TwitterSource", "RedditSource"]
```

### Step 4: Update server.py

Import the new source:
```python
from sources import TwitterSource, RedditSource

# In ResearchMCPServer.__init__():
self.reddit = RedditSource()
```

Add tools to `handle_list_tools()`:
```python
Tool(
    name="reddit_search_subreddit",
    description="Search Reddit posts in a subreddit",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "subreddit": {"type": "string", "description": "Subreddit name", "default": "all"},
            "count": {"type": "integer", "description": "Number of results", "default": 20}
        },
        "required": ["query"]
    }
)
```

Add handler method in `ResearchMCPServer`:
```python
async def _handle_reddit_tool(self, name: str, arguments: dict) -> List[types.TextContent]:
    """Dispatch Reddit tools"""
    operation = name.replace("reddit_", "")

    if operation == "search_subreddit":
        result = await self.reddit.search_subreddit(
            arguments["query"],
            arguments.get("subreddit", "all"),
            arguments.get("count", 20)
        )
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    # ... other operations
```

Update tool dispatcher in `handle_call_tool()`:
```python
elif name.startswith("reddit_"):
    return await self._handle_reddit_tool(name, arguments)
```

## Design Patterns

### Client Caching
Cache authenticated clients to avoid re-authentication:

```python
def __init__(self):
    self.authenticated_clients = {}

async def _get_authenticated_client(self, username: str, password: str):
    cache_key = username
    if cache_key in self.authenticated_clients:
        return self.authenticated_clients[cache_key]

    # Authenticate
    client = await authenticate(username, password)
    self.authenticated_clients[cache_key] = client
    return client
```

### Response Formatting
Keep responses consistent across sources:

```python
def _format_post(self, post: Any) -> Dict[str, Any]:
    """Format a post object into standardized dictionary"""
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author": post.author,
        "created_at": str(post.created_at),
        "engagement": {
            "likes": post.likes,
            "comments": post.comment_count,
            "shares": post.shares
        }
    }

def _format_posts(self, posts: List[Any]) -> List[Dict[str, Any]]:
    """Format multiple posts"""
    return [self._format_post(post) for post in posts]
```

### Error Handling
Consistent error handling:

```python
async def operation(self, param: str) -> Dict[str, Any]:
    try:
        # Implementation
        pass
    except AuthenticationError as e:
        raise ValueError(f"Authentication failed: {str(e)}")
    except APIError as e:
        raise ValueError(f"API error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {str(e)}")
```

## Tool Naming Convention

Use this convention for new tools:
- `{source}_{operation}_{target}` when applicable
- Examples:
  - `twitter_get_timeline` - Get timeline from Twitter
  - `reddit_search_subreddit` - Search within a subreddit
  - `reddit_get_post_comments` - Get comments on a post
  - `hacker_news_search_stories` - Search HN stories

## Testing Your Source

Before adding to main server:

```python
# test_new_source.py
import asyncio
from sources.new_source import NewSource

async def test():
    source = NewSource()
    result = await source.some_operation("test_param")
    print(result)

asyncio.run(test())
```

## Dependencies

Add required libraries to `requirements.txt`:
```
reddit-api-client>=1.0.0
hacker-news>=1.0.0
```

## Documentation

Update main README.md with:
1. Tool descriptions
2. Example API calls
3. Response format examples
4. Any authentication requirements

## Best Practices

1. **Async/Await** - All operations should be async for MCP compatibility
2. **Type Hints** - Use type hints for all parameters and return values
3. **Docstrings** - Document parameters, return types, and exceptions
4. **Caching** - Cache authenticated clients to improve performance
5. **Error Handling** - Raise `ValueError` with descriptive messages
6. **Formatting** - Return consistent JSON-serializable dictionaries
7. **Limits** - Enforce reasonable limits on result counts
8. **Secrets** - Never hardcode credentials; use environment variables or parameters

## Questions?

Refer to `twitter.py` for a complete, working example of source implementation.
