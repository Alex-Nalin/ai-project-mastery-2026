import asyncio
import anthropic
from openai import AsyncOpenAI

class ThinkingComparison:
    def __init__(self, anthropic_key: str, openai_key: str):
        self.anthropic = anthropic.AsyncAnthropic(api_key=anthropic_key)
        self.openai = AsyncOpenAI(api_key=openai_key)
    
    async def query_claude_thinking(self, problem: str):
        response = await self.anthropic.messages.create(
            model="claude-opus-4-8-2026-04-15",
            max_tokens=4096,
            thinking={"type": "enabled", "budget_tokens": 2048},
            messages=[{"role": "user", "content": problem}]
        )
        
        thinking = ""
        answer = ""
        for block in response.content:
            if block.type == "thinking":
                thinking = block.thinking
            elif block.type == "text":
                answer = block.text
        
        return {
            "model": "Claude Opus 4.8 (Extended Thinking)",
            "thinking_length": len(thinking),
            "answer": answer
        }
    
    async def query_gpt_thinking(self, problem: str):
        response = await self.openai.chat.completions.create(
            model="gpt-5.5-thinking-2026-04-01",
            messages=[{"role": "user", "content": problem}],
            reasoning_effort="high"
        )
        
        return {
            "model": "GPT-5.5 Pro",
            "answer": response.choices[0].message.content
        }
    
    async def compare(self, problem: str):
        results = await asyncio.gather(
            self.query_claude_thinking(problem),
            self.query_gpt_thinking(problem)
        )
        
        for result in results:
            print(f"\n=== {result['model']} ===")
            if 'thinking_length' in result:
                print(f"Thinking tokens: {result['thinking_length']}")
            print(f"Answer: {result['answer'][:300]}...")

async def main():
    comparator = ThinkingComparison(
        anthropic_key="your-key",
        openai_key="your-key"
    )
    
    problem = """A company has 3 manufacturing plants.
Plant A produces 40% of total output, with 2% defect rate.
Plant B produces 35% of total output, with 3% defect rate.
Plant C produces 25% of total output, with 1% defect rate.

If a randomly selected product is defective, what is the probability it came from Plant B?

Apply Bayes' theorem step by step."""
    
    await comparator.compare(problem)

asyncio.run(main())
