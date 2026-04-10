# Quick Setup Guide

Get research-mcp up and running in 5 minutes.

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Get Your Twitter Cookies

### On Your Computer:

1. Open [twitter.com](https://twitter.com) or [x.com](https://x.com) in your browser
2. **Log in to your account**
3. **Press F12** to open Developer Tools
4. Click the **"Application"** tab (or **"Storage"** in Firefox)
5. In the left sidebar, find **Cookies → twitter.com**
6. Look for these two cookies:
   - **ct0** - Copy the long string in the "Value" column
   - **auth_token** - Copy the long string in the "Value" column

### Visual Example:
```
Developer Tools
├── Application
│   └── Storage
│       └── Cookies
│           └── twitter.com
│               ├── ct0 ............... "abc123xyz..." ← Copy this
│               ├── auth_token ........ "def456uvw..." ← Copy this
│               └── (other cookies)
```

## 3. Create .env File

```bash
# Copy the example file
cp env_example.txt .env

# Edit it with your favorite editor
nano .env
# or
vim .env
# or open in VS Code, PyCharm, etc.
```

## 4. Add Your Cookies to .env

Replace the placeholder values:

```
TWITTER_CT0=abc123xyz...
TWITTER_AUTH_TOKEN=def456uvw...
```

**Save the file** (Ctrl+S or your editor's save command)

## 5. Test It Works

### Quick Manual Test (Recommended First):

```bash
python test_manual.py
```

You should see output like:

```
============================================================
  Research MCP - Twitter Source Tests
============================================================

============================================================
  TEST 1: Authentication
============================================================

✓ Authentication successful!
  Username: your_username
  Name: Your Name
  Followers: 1,234
  Verified: False

============================================================
  TEST 2: Get Timeline
============================================================

✓ Retrieved 3 timeline tweets
...
```

### Or With Pytest:

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

## 6. Run the Server

```bash
python server.py
```

The server is now running and ready for MCP client connections!

## Troubleshooting

### "Authentication failed" error:

- Cookies may have expired
- Solution: Get fresh cookies (repeat steps 1-4)

### "Twitter cookies not found in .env file" error:

- .env file doesn't exist or is missing values
- Solution:
  ```bash
  cp env_example.txt .env
  # Edit .env with your cookies
  ```

### "ModuleNotFoundError: No module named 'twikit'":

- Dependencies not installed
- Solution: `pip install -r requirements.txt`

### Can't find ct0 or auth_token cookies:

- Make sure you're looking at twitter.com cookies (not x.com)
- Make sure you're logged in
- Try refreshing the page and reopening DevTools

## Next Steps

- ✅ Tests passing? You're ready to use the server!
- 📖 See [README.md](README.md) for tool usage examples
- 🧪 See [TESTING.md](TESTING.md) for advanced testing
- 🔗 See [sources/README.md](sources/README.md) for adding new sources (Reddit, etc.)

## Quick Command Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Run manual tests
python test_manual.py

# Run pytest tests
pytest tests/ -v

# Start the server
python server.py

# View logs
tail -f research-mcp.log
```

## Security Reminders

- ⚠️ **Never commit .env to git** (it's in .gitignore)
- ⚠️ **Never share your cookies** - they give access to your account
- ⚠️ **Cookies expire** - you'll need fresh ones after a few weeks
- ⚠️ **Keep .env private** - treat it like a password

That's it! You're all set. 🚀
