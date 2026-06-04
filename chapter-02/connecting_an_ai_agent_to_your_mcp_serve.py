import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def connect_to_mcp_server():
    """Connect to MCP server and use its tools."""
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Call a tool
            result = await session.call_tool(
                "get_customer",
                {"customer_id": 1}
            )
            print(f"\nCustomer result: {result.content[0].text}")
            
            # Get analytics
            analytics = await session.call_tool("get_analytics", {})
            print(f"\nAnalytics: {analytics.content[0].text}")

asyncio.run(connect_to_mcp_server())
