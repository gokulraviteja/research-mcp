# Testing Guide for Research MCP

This document explains how to test the research-mcp server before using it in production.

## Setup

### 1. Install Test Dependencies

For manual testing (no extra dependencies needed beyond requirements.txt):
```bash
pip install -r requirements.txt
```

For pytest unit tests:
```bash
pip install -r requirements.txt pytest pytest-asyncio
```

### 2. Get Twitter Cookies

Both test approaches require valid Twitter cookies:

1. Go to [twitter.com](https://twitter.com) and log in
2. Open Developer Tools (F12)
3. Navigate to: **Application/Storage → Cookies → twitter.com**
4. Find and copy these values:
   - `ct0` - CSRF token
   - `auth_token` - Session token

These cookies are needed because the TwitterSource uses cookie-based authentication.

## Approach 1: Manual Testing (Recommended First)

Quick way to verify everything works. No pytest setup needed.

### Steps

1. **Create `.env` file from template:**
```bash
cp env_example.txt .env
```

2. **Add your Twitter cookies to `.env`:**
```
TWITTER_CT0=your_ct0_value_here
TWITTER_AUTH_TOKEN=your_auth_token_value_here
```

3. **Run the test script:**
```bash
python test_manual.py
```

3. Watch the output for test results:

```
============================================================
  Research MCP - Twitter Source Tests
============================================================

============================================================
  TEST 1: Authentication
============================================================

✓ Authentication successful!
  Username: example_user
  Name: Example User
  Followers: 1,234
  Verified: True

...more tests...

============================================================
  TEST SUMMARY
============================================================

  ✓ PASS   - Authentication
  ✓ PASS   - Get Timeline
  ✓ PASS   - Get Latest Timeline
  ✓ PASS   - Search Tweets
  ✓ PASS   - Get Single Tweet
  ✓ PASS   - Get Tweet Replies
  ✓ PASS   - Client Caching

Total: 7/7 tests passed

🎉 All tests passed! Server is ready to use.
```

### What It Tests

The manual test covers:

1. **Authentication** - Verify cookies work and get user info
2. **Get Timeline** - Fetch your home timeline
3. **Get Latest Timeline** - Fetch latest/chronological timeline
4. **Search Tweets** - Search for tweets with query
5. **Get Single Tweet** - Fetch a specific tweet by ID
6. **Get Tweet Replies** - Get replies to a tweet
7. **Client Caching** - Verify authenticated clients are cached

### Troubleshooting Manual Tests

**"Authentication failed"**
- Cookies may be expired (reload twitter.com and copy fresh cookies)
- Verify both `ct0` and `auth_token` are set correctly
- Check for leading/trailing whitespace in cookie values

**"No results from search"**
- Twitter's unofficial API may be rate-limited
- Try a simpler search query
- Wait a minute and try again

**"Tweet not found"**
- The tweet may have been deleted
- The search might not return tweets with replies
- This is normal and expected

## Approach 2: Pytest Unit Tests

For more comprehensive testing and CI/CD integration.

### Setup

```bash
pip install -r requirements.txt pytest pytest-asyncio
```

### Configure Tests

Your `.env` file (created in Approach 1) is automatically used by pytest. Just make sure it has your cookies:

```bash
# .env should contain:
TWITTER_CT0=your_ct0_value_here
TWITTER_AUTH_TOKEN=your_auth_token_value_here
```

### Run All Tests

```bash
pytest tests/ -v
```

Output:
```
tests/test_twitter_source.py::TestTwitterSourceUnit::test_authenticate_valid_cookies PASSED
tests/test_twitter_source.py::TestTwitterSourceUnit::test_authenticate_invalid_cookies PASSED
tests/test_twitter_source.py::TestTwitterSourceUnit::test_get_timeline PASSED
tests/test_twitter_source.py::TestTwitterSourceUnit::test_get_latest_timeline PASSED
...
```

### Run Specific Test

```bash
# Run only authentication tests
pytest tests/test_twitter_source.py::TestTwitterSourceUnit::test_authenticate_valid_cookies -v

# Run only integration tests
pytest tests/test_twitter_source.py::TestTwitterSourceIntegration -v

# Run with output
pytest tests/ -v -s
```

### Run with Coverage

```bash
pip install pytest-cov
pytest tests/ --cov=sources --cov-report=html
# Open htmlcov/index.html in browser
```

### Test Categories

**Unit Tests** (`TestTwitterSourceUnit`):
- Individual method testing
- Valid/invalid input handling
- Response structure validation
- Error cases

**Integration Tests** (`TestTwitterSourceIntegration`):
- Multi-step workflows
- Real-world usage patterns
- Data consistency across calls

## Approach 3: Running the Server

Once tests pass, run the actual server:

### 1. Start the Server

```bash
python server.py
```

You should see it running on stdio waiting for MCP client connections.

### 2. Connect with MCP Client

Use an MCP client to send tool calls. Example:

```json
{
  "tool": "twitter_authenticate",
  "arguments": {
    "ct0": "your_ct0_cookie",
    "auth_token": "your_auth_token"
  }
}
```

### 3. Test Each Tool

Call each of the 6 tools to verify they work:
- `twitter_authenticate`
- `twitter_get_timeline`
- `twitter_get_latest_timeline`
- `twitter_search_tweets`
- `twitter_get_tweet`
- `twitter_get_tweet_replies`

## CI/CD Integration

To add automatic testing to your git workflow:

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Test Research MCP

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt pytest pytest-asyncio
      - run: pytest tests/ -v
```

Note: You'll need to add secrets for Twitter cookies in GitHub Settings.

## Testing Checklist

Before deploying to production:

- [ ] Manual test passes (all 7 tests)
- [ ] pytest unit tests pass
- [ ] All 6 Twitter tools work
- [ ] Authentication with real cookies works
- [ ] Search returns results
- [ ] Timeline tweets display correctly
- [ ] Tweet replies load properly
- [ ] Client caching works (verified in logs)
- [ ] No memory leaks (long-running test)
- [ ] Error handling works (test with invalid cookies)

## Performance Testing

For longer-running tests:

```python
# In test_manual.py or custom script
import time

start = time.time()
await twitter.search_tweets(CT0, AUTH_TOKEN, "test", count=50)
elapsed = time.time() - start
print(f"Search took {elapsed:.2f}s")
```

Typical performance:
- Authentication: < 2s
- Search: 1-3s (depends on query)
- Timeline: 1-2s
- Single tweet: < 1s
- Replies: 1-2s

## Security Notes

- **Never commit test cookies** to git (always use .gitignore)
- **Rotate cookies regularly** - Twitter sessions expire
- **Use environment variables** for CI/CD testing:
  ```bash
  export CT0="your_cookie"
  export AUTH_TOKEN="your_token"
  pytest tests/ -v
  ```

## Debugging Failed Tests

### Enable detailed output:
```bash
pytest tests/ -vv -s --tb=long
```

### Check cookie validity:
```python
from sources.twitter import TwitterSource
import asyncio

async def test():
    twitter = TwitterSource()
    try:
        result = await twitter.authenticate(CT0, AUTH_TOKEN)
        print(result)
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
```

### Check network connectivity:
```bash
# Verify Twitter is accessible
curl https://twitter.com
```

## Common Issues

### "ValueError: Authentication failed"
- Cookies are expired or invalid
- Solution: Get fresh cookies from twitter.com

### "No module named 'sources'"
- PYTHONPATH not set correctly
- Solution: Run tests from project root: `cd /path/to/research-mcp && pytest tests/`

### Rate limiting
- Twitter may limit requests
- Solution: Wait a few minutes between test runs

### Async errors
- pytest-asyncio not installed
- Solution: `pip install pytest-asyncio`

## Next Steps

After tests pass:
1. Review the results
2. Check error messages if any test fails
3. Address any issues (usually cookie-related)
4. Run the server: `python server.py`
5. Integrate with your MCP client

Happy testing! 🚀
