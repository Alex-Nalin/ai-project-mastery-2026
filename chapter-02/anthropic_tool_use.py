import anthropic

client = anthropic.Anthropic(api_key="your-key")

tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name"
                },
                "units": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["location"]
        }
    }
]

response = client.messages.create(
    model="claude-opus-4-8-2026-04-15",
    max_tokens=4096,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}]
)

# Tool calls come as content blocks
for content in response.content:
    if content.type == "tool_use":
        print(f"Tool: {content.name}")
        print(f"Input: {content.input}")
