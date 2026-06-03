from openai import OpenAI

client = OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-5.5-thinking-2026-04-01",
    messages=[
        {
            "role": "user",
            "content": "What is the probability of rolling a sum of 7 with two fair dice? Show your reasoning."
        }
    ],
    reasoning_effort="high",  # Controls how many reasoning paths to explore
    temperature=0.2
)

print(response.choices[0].message.content)
