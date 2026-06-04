"""
Test script for MCP server connection.
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp_server():
    """Test all tools and resources from the MCP server."""
    server_params = StdioServerParameters(
        command="python",
        args=["customer_mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # Test resource listing
            resources = await session.list_resources()
            print("Available resources:")
            for resource in resources.resources:
                print(f"  - {resource.name}: {resource.uri}")
            
            # Test tool listing
            tools = await session.list_tools()
            print("\nAvailable tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test get_customer tool
            print("\nTesting get_customer...")
            result = await session.call_tool("get_customer", {"customer_id": 1})
            print(f"Result: {result.content[0].text}")
            
            # Test search_customers tool
            print("\nTesting search_customers...")
            result = await session.call_tool("search_customers", {"query": "Alice"})
            print(f"Result: {result.content[0].text}")
            
            # Test analytics
            print("\nTesting get_analytics...")
            result = await session.call_tool("get_analytics", {})
            print(f"Result: {result.content[0].text}")

asyncio.run(test_mcp_server())
