from openai import OpenAI

client = OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-5.5-thinking-2026-04-01",
    messages=[
        {
            "role": "system",
            "content": """You are a reasoning system that follows a strict process:

STAGE 1: Problem Decomposition
- Break the problem into independent sub-problems
- Identify dependencies between sub-problems

STAGE 2: Solve Each Sub-Problem
- Work through each sub-problem sequentially
- Show all intermediate calculations
- Label each result clearly

STAGE 3: Verification
- Check each calculation for errors
- Verify assumptions against the original problem

STAGE 4: Final Answer
- Combine all sub-problem results
- Present the answer in a clear, concise format

Always complete all four stages."""
        },
        {
            "role": "user",
            "content": """A factory produces 2,847 widgets per day.
They operate 6 days per week.
Each widget sells for $12.50.
Raw materials cost $4.30 per widget.
Labor costs $2,800 per day.
Rent and overhead are $15,000 per month (assume 4 weeks per month).

Calculate the monthly profit."""
        }
    ],
    temperature=0.2,
    reasoning_effort="high"
)

print(response.choices[0].message.content)
