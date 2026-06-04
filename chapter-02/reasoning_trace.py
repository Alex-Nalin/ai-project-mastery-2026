import asyncio
from typing import List, Dict, Any
from pydantic import BaseModel
from openai import AsyncOpenAI
import anthropic
import google.generativeai as genai
import json

class ReasoningTrace(BaseModel):
    model: str
    reasoning: str
    answer: str
    confidence: float = 0.0
    
class AggregatedResult(BaseModel):
    final_answer: str
    confidence_score: float
    model_agreement: float
    traces: List[ReasoningTrace]

class SelfConsistencyPipeline:
    def __init__(
        self,
        openai_key: str,
        anthropic_key: str,
        gemini_key: str
    ):
        self.openai_client = AsyncOpenAI(api_key=openai_key)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_key)
        genai.configure(api_key=gemini_key)
        self.gemini_model = genai.GenerativeModel('gemini-3.5-pro-001')
        
    async def query_gpt55_thinking(self, prompt: str) -> ReasoningTrace:
        """Query GPT-5.5 Pro with extended reasoning."""
        response = await self.openai_client.chat.completions.create(
            model="gpt-5.5-thinking-2026-04-01",
            messages=[
                {
                    "role": "system",
                    "content": "You are a careful reasoning system. Think step by step, then provide your final answer."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            reasoning_effort="high"
        )
        
        content = response.choices[0].message.content
        # Extract reasoning and answer (assuming structured format)
        parts = content.split("Final Answer:")
        reasoning = parts[0].strip() if len(parts) > 1 else content
        answer = parts[1].strip() if len(parts) > 1 else content
        
        return ReasoningTrace(
            model="GPT-5.5 Pro",
            reasoning=reasoning,
            answer=answer,
            confidence=0.9
        )
    
    async def query_claude_opus47(self, prompt: str) -> ReasoningTrace:
        """Query Claude Opus 4.8 with extended thinking."""
        response = await self.anthropic_client.messages.create(
            model="claude-opus-4-8-2026-04-15",
            max_tokens=4096,
            thinking={
                "type": "enabled",
                "budget_tokens": 2048
            },
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\nPlease show your extended thinking process, then provide your final answer."
                }
            ]
        )
        
        # Extract thinking and answer from Claude's response
        thinking_content = ""
        answer_content = ""
        
        for block in response.content:
            if block.type == "thinking":
                thinking_content = block.thinking
            elif block.type == "text":
                answer_content = block.text
        
        return ReasoningTrace(
            model="Claude Opus 4.8",
            reasoning=thinking_content,
            answer=answer_content,
            confidence=0.95
        )
    
    async def query_gemini31_pro(self, prompt: str) -> ReasoningTrace:
        """Query Gemini 3.5 Pro."""
        response = await self.gemini_model.generate_content_async(
            prompt,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "max_output_tokens": 4096,
            }
        )
        
        content = response.text
        # Simple split approach
        parts = content.split("Final Answer:")
        reasoning = parts[0].strip() if len(parts) > 1 else content
        answer = parts[1].strip() if len(parts) > 1 else content
        
        return ReasoningTrace(
            model="Gemini 3.5 Pro",
            reasoning=reasoning,
            answer=answer,
            confidence=0.85
        )
    
    async def aggregate_answers(
        self, 
        traces: List[ReasoningTrace]
    ) -> AggregatedResult:
        """Aggregate answers using weighted majority voting."""
        # Simple majority voting for now
        answers = [t.answer.lower().strip() for t in traces]
        
        # Count votes
        from collections import Counter
        vote_counts = Counter(answers)
        most_common = vote_counts.most_common(1)[0]
        
        # Calculate agreement
        total_votes = len(traces)
        agreement = most_common[1] / total_votes
        
        # Confidence is weighted by model confidence
        weighted_confidence = sum(
            t.confidence for t in traces 
            if t.answer.lower().strip() == most_common[0]
        ) / total_votes
        
        return AggregatedResult(
            final_answer=most_common[0],
            confidence_score=weighted_confidence,
            model_agreement=agreement,
            traces=traces
        )
    
    async def run(self, prompt: str) -> AggregatedResult:
        """Run the full self-consistency pipeline."""
        # Query all models in parallel
        tasks = [
            self.query_gpt55_thinking(prompt),
            self.query_claude_opus47(prompt),
            self.query_gemini31_pro(prompt)
        ]
        
        traces = await asyncio.gather(*tasks)
        result = await self.aggregate_answers(traces)
        
        return result

# Usage
async def main():
    pipeline = SelfConsistencyPipeline(
        openai_key="your-openai-key",
        anthropic_key="your-anthropic-key",
        gemini_key="your-gemini-key"
    )
    
    prompt = """A company has 150 employees. 60% work in engineering, 
25% in sales, and the rest in operations. 
Engineering gets 3 vacation weeks per year, sales gets 4, operations gets 2.
What is the total number of vacation weeks for all employees combined?

Think step by step and provide your final answer after 'Final Answer:'"""
    
    result = await pipeline.run(prompt)
    
    print(f"Final Answer: {result.final_answer}")
    print(f"Confidence: {result.confidence_score:.2%}")
    print(f"Model Agreement: {result.model_agreement:.2%}")
    
    for trace in result.traces:
        print(f"\n--- {trace.model} ---")
        print(f"Reasoning: {trace.reasoning[:200]}...")
        print(f"Answer: {trace.answer}")

asyncio.run(main())
