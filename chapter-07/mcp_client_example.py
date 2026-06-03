# mcp_client_example.py
"""Query MCP knowledge base from any agent."""

from mcp import Client
from mcp.client.stdio import stdio_client


async def query_knowledge_base(query: str, top_k: int = 5) -> dict:
    """Query the MCP knowledge base server."""
    async with stdio_client(
        command="python",
        args=["/path/to/mcp_knowledge_server/server.py"],
    ) as (read, write):
        async with Client(read, write) as client:
            # Initialize connection
            await client.initialize()

            # Query the knowledge base
            result = await client.call_tool(
                "query_knowledge_base",
                {"query": query, "top_k": top_k},
            )

            return result.content[0].text


# Usage
# import asyncio
# result = await query_knowledge_base(
#     "What are our data retention policies?"
# )
# print(result)
