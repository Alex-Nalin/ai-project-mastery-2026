# connect_to_mcp.py
from mcp import MCPClient
from anthropic import AsyncAnthropic

class MCPEnabledAgent:
    def __init__(self, mcp_server_url: str, anthropic_key: str):
        self.mcp_client = MCPClient(mcp_server_url)
        self.llm = AsyncAnthropic(api_key=anthropic_key)
    
    async def run(self, task: str) -> str:
        # Step 1: Discover available tools
        tools = await self.mcp_client.discover_tools()
        
        # Step 2: Let the model plan with tool awareness
        response = await self.llm.messages.create(
            model="claude-opus-4.8",
            max_tokens=4000,
            system=f"You have access to these tools: {json.dumps(tools)}",
            messages=[{
                "role": "user",
                "content": task
            }]
        )
        
        # Step 3: Execute any tool calls the model requests
        if response.stop_reason == "tool_use":
            for tool_call in response.content:
                if tool_call.type == "tool_use":
                    result = await self.mcp_client.execute_tool(
                        tool_call.name,
                        tool_call.input
                    )
                    # Feed results back to model
                    response = await self.llm.messages.create(
                        model="claude-opus-4.8",
                        messages=[...]  # Include tool results
                    )
        
        return response.content[0].text

# Usage
agent = MCPEnabledAgent(
    mcp_server_url="http://localhost:8080",
    anthropic_key="sk-ant-..."
)

result = await agent.run("Research the latest AI breakthroughs and save them to the database")
