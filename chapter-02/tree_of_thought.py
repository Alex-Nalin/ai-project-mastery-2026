import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key="your-api-key")

class TreeOfThought:
    def __init__(self, model="gpt-5.5-thinking-2026-04-01"):
        self.model = model
        self.branches = []
    
    async def generate_branches(self, problem, num_branches=3):
        """Generate multiple reasoning branches."""
        tasks = []
        for i in range(num_branches):
            prompt = f"""Problem: {problem}

You are exploring reasoning path {i+1}/{num_branches}.
Consider a different approach to this problem.
Show your complete reasoning step by step.

Branch {i+1}:"""
            tasks.append(self._query_model(prompt))
        
        responses = await asyncio.gather(*tasks)
        self.branches = responses
        return responses
    
    async def evaluate_branches(self):
        """Evaluate and compare reasoning paths."""
        branches_text = "\n\n".join([
            f"Branch {i+1}:\n{b}" 
            for i, b in enumerate(self.branches)
        ])
        
        prompt = f"""Evaluate these reasoning branches for correctness and completeness:

{branches_text}

For each branch:
1. Identify any logical errors
2. Note missing steps or assumptions
3. Rate confidence (1-10)
4. Determine if the final answer is correct

Then select the best branch and explain why."""
        
        return await self._query_model(prompt)
    
    async def _query_model(self, prompt):
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            reasoning_effort="high"
        )
        return response.choices[0].message.content

# Usage
async def main():
    tot = TreeOfThought()
    problem = "A train leaves New York at 60 mph. Another train leaves Boston at 70 mph. Distance between cities is 215 miles. When and where do they meet?"
    
    branches = await tot.generate_branches(problem, num_branches=3)
    evaluation = await tot.evaluate_branches()
    
    print("=== Branches ===")
    for i, b in enumerate(branches):
        print(f"\nBranch {i+1}:")
        print(b[:200] + "...")
    
    print("\n=== Evaluation ===")
    print(evaluation)

asyncio.run(main())
