import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

response = client.messages.create(
    model="claude-opus-4-8-2026-04-15",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": """A company has 3,847 customers. 
They want to split them into groups of 47 for training sessions.
How many full groups can they form, and how many customers will be left over?

Think step by step, showing your work."""
        }
    ]
)

print(response.content[0].text)
