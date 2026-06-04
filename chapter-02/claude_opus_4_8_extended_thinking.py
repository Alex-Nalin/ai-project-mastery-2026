import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

response = client.messages.create(
    model="claude-opus-4-8-2026-04-15",
    max_tokens=4096,
    thinking={
        "type": "enabled",
        "budget_tokens": 2048  # How many tokens to allocate for thinking
    },
    messages=[
        {
            "role": "user",
            "content": """Design a distributed system that can handle 1 million concurrent WebSocket connections. 
Consider: load balancing, message queuing, fault tolerance, and scaling strategy.

Think through this carefully before answering."""
        }
    ]
)

# The response contains both thinking and final answer blocks
for block in response.content:
    if block.type == "thinking":
        print("=== THINKING PROCESS ===")
        print(block.thinking[:500] + "...")
    elif block.type == "text":
        print("=== FINAL ANSWER ===")
        print(block.text)
