#!/usr/bin/env python3
"""
Research MCP Server

Provides access to multiple research sources (Twitter, Reddit, etc.) through
the Model Context Protocol. Extensible architecture for adding new sources.
"""

import asyncio
import json
from typing import Any, Dict, List

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent, LoggingLevel
import mcp.types as types

from sources import TwitterSource


class ResearchMCPServer:
    """Main MCP server that dispatches to source-specific implementations"""

    def __init__(self):
        """Initialize the research MCP server with sources"""
        self.server = Server("research-mcp")
        self.twitter = TwitterSource()
        self.setup_handlers()

    def setup_handlers(self):
        """Register MCP server handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools across sources"""
            return [
                # Twitter tools
                Tool(
                    name="twitter_authenticate",
                    description="Test Twitter authentication and get user info",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ct0": {
                                "type": "string",
                                "description": "Twitter CSRF token cookie (required)"
                            },
                            "auth_token": {
                                "type": "string",
                                "description": "Twitter auth token cookie (required)"
                            }
                        },
                        "required": ["ct0", "auth_token"]
                    }
                ),
                Tool(
                    name="twitter_get_timeline",
                    description="Get tweets from your Twitter timeline",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "count": {
                                "type": "integer",
                                "description": "Number of tweets to retrieve (default: 20)",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "ct0": {
                                "type": "string",
                                "description": "Twitter CSRF token cookie (required)"
                            },
                            "auth_token": {
                                "type": "string",
                                "description": "Twitter auth token cookie (required)"
                            }
                        },
                        "required": ["ct0", "auth_token"]
                    }
                ),
                Tool(
                    name="twitter_get_latest_timeline",
                    description="Get latest tweets from your Twitter timeline",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "count": {
                                "type": "integer",
                                "description": "Number of tweets to retrieve (default: 20)",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "ct0": {
                                "type": "string",
                                "description": "Twitter CSRF token cookie (required)"
                            },
                            "auth_token": {
                                "type": "string",
                                "description": "Twitter auth token cookie (required)"
                            }
                        },
                        "required": ["ct0", "auth_token"]
                    }
                ),
                Tool(
                    name="twitter_search_tweets",
                    description="Search for tweets on Twitter",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query string"
                            },
                            "count": {
                                "type": "integer",
                                "description": "Number of tweets to retrieve (default: 20)",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "product": {
                                "type": "string",
                                "description": "Type of results to return",
                                "enum": ["Top", "Latest"],
                                "default": "Latest"
                            },
                            "ct0": {
                                "type": "string",
                                "description": "Twitter CSRF token cookie (required)"
                            },
                            "auth_token": {
                                "type": "string",
                                "description": "Twitter auth token cookie (required)"
                            }
                        },
                        "required": ["query", "ct0", "auth_token"]
                    }
                ),
                Tool(
                    name="twitter_get_tweet",
                    description="Get a specific tweet by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {
                                "type": "string",
                                "description": "The ID of the tweet to retrieve"
                            },
                            "ct0": {
                                "type": "string",
                                "description": "Twitter CSRF token cookie (required)"
                            },
                            "auth_token": {
                                "type": "string",
                                "description": "Twitter auth token cookie (required)"
                            }
                        },
                        "required": ["tweet_id", "ct0", "auth_token"]
                    }
                ),
                Tool(
                    name="twitter_get_tweet_replies",
                    description="Get replies to a specific tweet",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "tweet_id": {
                                "type": "string",
                                "description": "The ID of the tweet to get replies for"
                            },
                            "count": {
                                "type": "integer",
                                "description": "Number of replies to retrieve (default: 20)",
                                "default": 20,
                                "minimum": 1,
                                "maximum": 100
                            },
                            "ct0": {
                                "type": "string",
                                "description": "Twitter CSRF token cookie (required)"
                            },
                            "auth_token": {
                                "type": "string",
                                "description": "Twitter auth token cookie (required)"
                            }
                        },
                        "required": ["tweet_id", "ct0", "auth_token"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
            """Handle tool calls by dispatching to appropriate source"""
            try:
                # Dispatch to appropriate source based on tool name prefix
                if name.startswith("twitter_"):
                    return await self._handle_twitter_tool(name, arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_twitter_tool(self, name: str, arguments: dict) -> List[types.TextContent]:
        """Dispatch Twitter tools to TwitterSource"""
        # Extract credentials
        ct0 = arguments.get("ct0")
        auth_token = arguments.get("auth_token")
        if not ct0 or not auth_token:
            return [types.TextContent(type="text", text="Error: Both ct0 and auth_token are required")]

        # Extract tool operation (twitter_OPERATION)
        operation = name.replace("twitter_", "")

        try:
            if operation == "authenticate":
                result = await self.twitter.authenticate(ct0, auth_token)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif operation == "get_timeline":
                count = arguments.get("count", 20)
                result = await self.twitter.get_timeline(ct0, auth_token, count)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif operation == "get_latest_timeline":
                count = arguments.get("count", 20)
                result = await self.twitter.get_latest_timeline(ct0, auth_token, count)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif operation == "search_tweets":
                count = arguments.get("count", 20)
                product = arguments.get("product", "Latest")
                result = await self.twitter.search_tweets(ct0, auth_token, arguments["query"], count, product)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif operation == "get_tweet":
                result = await self.twitter.get_tweet(ct0, auth_token, arguments["tweet_id"])
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif operation == "get_tweet_replies":
                count = arguments.get("count", 20)
                result = await self.twitter.get_tweet_replies(ct0, auth_token, arguments["tweet_id"], count)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            else:
                raise ValueError(f"Unknown Twitter operation: {operation}")

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="research-mcp",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point"""
    server = ResearchMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
