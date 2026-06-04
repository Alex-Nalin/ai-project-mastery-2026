"""
Self-Consistency Reasoning Pipeline
Queries multiple models and aggregates answers using weighted voting.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from collections import Counter
from pydantic import BaseModel, Field

# Model imports
from openai import AsyncOpenAI
import anthropic
import google.generativeai as genai

# ===========================================================

# Data Models
# ============================================================

class ReasoningStep(BaseModel):
    step_number: int
    description: str
    result: str
    
class ModelResponse(BaseModel):
    model_name: str
    reasoning_steps: List[ReasoningStep]
    final_answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    thinking_time_ms: int = 0
    
class AggregatedResult(BaseModel):
    question: str
    final_answer: str
    confidence_score: float
    model_agreement: float
    responses: List[ModelResponse]
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# ============================================================
# Model Clients
# ============================================================

class ModelClient:
    """Base class for model clients."""
    
    async def query(self, question: str) -> ModelResponse:
        raise NotImplementedError

class GPT55ThinkingClient(ModelClient):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def query(self, question: str) -> ModelResponse:
        start_time = datetime.now()
        
        response = await self.client.chat.completions.create(
            model="gpt-5.5-thinking-2026-04-01",
            messages=[
                {
                    "role": "system",
                    "content": """You are a reasoning system. Work through problems step by step.
For each step, clearly state what you're doing and the result.
End with 'FINAL ANSWER:' followed by your conclusion."""
                },
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            reasoning_effort="high"
        )
        
        thinking_time = (datetime.now() - start_time).total_seconds() * 1000
        content = response.choices[0].message.content
        
        return self._parse_response(content, thinking_time)
    
    def _parse_response(self, content: str, thinking_time: float) -> ModelResponse:
        steps = []
        lines = content.split('\n')
        current_step = 1
        current_desc = []
        
        for line in lines:
            if line.startswith('FINAL ANSWER:'):
                final_answer = line.replace('FINAL ANSWER:', '').strip()
                break
            elif line.strip().startswith(f'{current_step}.'):
                if current_desc:
                    steps.append(ReasoningStep(
                        step_number=current_step,
                        description=' '.join(current_desc),
                        result=current_desc[-1] if current_desc else ''
                    ))
                    current_step += 1
                    current_desc = [line]
            else:
                current_desc.append(line)
        else:
            final_answer = content.split('FINAL ANSWER:')[-1].strip() if 'FINAL ANSWER:' in content else content
        
        return ModelResponse(
            model_name="GPT-5.5 Pro",
            reasoning_steps=steps,
            final_answer=final_answer,
            confidence=0.9,
            thinking_time_ms=int(thinking_time)
        )

class ClaudeOpus47Client(ModelClient):
    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def query(self, question: str) -> ModelResponse:
        start_time = datetime.now()
        
        response = await self.client.messages.create(
            model="claude-opus-4-8-2026-04-15",
            max_tokens=4096,
            thinking={"type": "enabled", "budget_tokens": 2048},
            messages=[
                {
                    "role": "user",
                    "content": f"{question}\n\nPlease work through this step by step and end with 'FINAL ANSWER:' followed by your conclusion."
                }
            ]
        )
        
        thinking_time = (datetime.now() - start_time).total_seconds() * 1000
        
        thinking_content = ""
        answer_content = ""
        
        for block in response.content:
            if block.type == "thinking":
                thinking_content = block.thinking
            elif block.type == "text":
                answer_content = block.text
        
        return self._parse_response(thinking_content, answer_content, thinking_time)
    
    def _parse_response(self, thinking: str, answer: str, thinking_time: float) -> ModelResponse:
        # Extract reasoning steps from thinking content
        steps = []
        lines = thinking.split('\n')
        step_num = 1
        
        for line in lines:
            if line.strip() and any(line.strip().startswith(str(i) + '.') for i in range(1, 20)):
                steps.append(ReasoningStep(
                    step_number=step_num,
                    description=line.strip(),
                    result=""
                ))
                step_num += 1
        
        # Extract final answer
        final_answer = answer
        if 'FINAL ANSWER:' in answer:
            final_answer = answer.split('FINAL ANSWER:')[-1].strip()
        
        return ModelResponse(
            model_name="Claude Opus 4.8",
            reasoning_steps=steps,
            final_answer=final_answer,
            confidence=0.95,
            thinking_time_ms=int(thinking_time)
        )

class Gemini31ProClient(ModelClient):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.5-pro-001')
    
    async def query(self, question: str) -> ModelResponse:
        start_time = datetime.now()
        
        response = await self.model.generate_content_async(
            f"{question}\n\nWork through this step by step. End with 'FINAL ANSWER:' followed by your conclusion.",
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "max_output_tokens": 4096,
            }
        )
        
        thinking_time = (datetime.now() - start_time).total_seconds() * 1000
        content = response.text
        
        return self._parse_response(content, thinking_time)
    
    def _parse_response(self, content: str, thinking_time: float) -> ModelResponse:
        steps = []
        lines = content.split('\n')
        step_num = 1
        
        for line in lines:
            if line.strip() and any(line.strip().startswith(f'{i}.') for i in range(1, 20)):
                steps.append(ReasoningStep(
                    step_number=step_num,
                    description=line.strip(),
                    result=""
                ))
                step_num += 1
        
        final_answer = content
        if 'FINAL ANSWER:' in content:
            final_answer = content.split('FINAL ANSWER:')[-1].strip()
        
        return ModelResponse(
            model_name="Gemini 3.5 Pro",
            reasoning_steps=steps,
            final_answer=final_answer,
            confidence=0.85,
            thinking_time_ms=int(thinking_time)
        )

# ============================================================
# Aggregation Engine
# ============================================================

class AggregationEngine:
    """Aggregates multiple model responses using weighted voting."""
    
    def __init__(self):
        self.weight_map = {
            "GPT-5.5 Pro": 1.0,
            "Claude Opus 4.8": 1.1,  # Slightly higher weight for extended thinking
            "Gemini 3.5 Pro": 0.9
        }
    
    def aggregate(self, responses: List[ModelResponse]) -> AggregatedResult:
        """Aggregate responses using weighted majority voting."""
        # Extract answers and weights
        answers = []
        weights = []
        
        for response in responses:
            answers.append(response.final_answer.lower().strip())
            weights.append(
                self.weight_map.get(response.model_name, 1.0) * response.confidence
            )
        
        # Weighted voting
        answer_weights = Counter()
        for answer, weight in zip(answers, weights):
            answer_weights[answer] += weight
        
        # Find winning answer
        winning_answer, winning_weight = answer_weights.most_common(1)[0]
        total_weight = sum(weights)
        
        # Calculate metrics
        confidence_score = winning_weight / total_weight
        model_agreement = len([a for a in answers if a == winning_answer]) / len(answers)
        
        return AggregatedResult(
            question=responses[0].reasoning_steps[0].description if responses[0].reasoning_steps else "",
            final_answer=winning_answer,
            confidence_score=confidence_score,
            model_agreement=model_agreement,
            responses=responses
        )

# ============================================================
# Main Pipeline
# ============================================================

class SelfConsistencyPipeline:
    """Main pipeline orchestrating multi-model reasoning and aggregation."""
    
    def __init__(self, openai_key: str, anthropic_key: str, gemini_key: str):
        self.clients = [
            GPT55ThinkingClient(openai_key),
            ClaudeOpus47Client(anthropic_key),
            Gemini31ProClient(gemini_key)
        ]
        self.aggregator = AggregationEngine()
    
    async def run(self, question: str) -> AggregatedResult:
        """Run the full self-consistency pipeline."""
        print(f"Querying {len(self.clients)} models in parallel...")
        
        # Query all models concurrently
        tasks = [client.query(question) for client in self.clients]
        responses = await asyncio.gather(*tasks)
        
        print("Aggregating results...")
        result = self.aggregator.aggregate(responses)
        
        return result

# ============================================================
# Usage Example
# ============================================================

async def main():
    pipeline = SelfConsistencyPipeline(
        openai_key="your-openai-key",
        anthropic_key="your-anthropic-key",
        gemini_key="your-gemini-key"
    )
    
    question = """A company has 3 manufacturing plants.
Plant A produces 40% of total output, with 2% defect rate.
Plant B produces 35% of total output, with 3% defect rate.
Plant C produces 25% of total output, with 1% defect rate.

If a randomly selected product is defective, what is the probability it came from Plant B?

Apply Bayes' theorem step by step."""
    
    result = await pipeline.run(question)
    
    print(f"\n{'='*60}")
    print(f"QUESTION: {question[:100]}...")
    print(f"{'='*60}")
    
    print(f"\nFINAL ANSWER: {result.final_answer}")
    print(f"CONFIDENCE: {result.confidence_score:.2%}")
    print(f"MODEL AGREEMENT: {result.model_agreement:.2%}")
    
    print(f"\n{'='*60}")
    print("INDIVIDUAL RESPONSES:")
    print(f"{'='*60}")
    
    for response in result.responses:
        print(f"\n--- {response.model_name} ---")
        print(f"Thinking Time: {response.thinking_time_ms}ms")
        print(f"Answer: {response.final_answer[:200]}...")
        print(f"Confidence: {response.confidence:.2%}")

if __name__ == "__main__":
    asyncio.run(main())
