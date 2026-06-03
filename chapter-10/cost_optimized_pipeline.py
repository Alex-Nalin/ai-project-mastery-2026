# cost_optimized_pipeline.py
from typing import Dict, List, Optional
import asyncio
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class QueryCost:
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    latency_ms: float
    source: str  # "local", "cloud_economy", "cloud_frontier"

class CostOptimizedPipeline:
    def __init__(self, local_model, economy_client, frontier_client):
        self.local = local_model
        self.economy = economy_client  # DeepSeek or Qwen
        self.frontier = frontier_client  # Claude or GPT
        self.cost_log: List[QueryCost] = []
        self.total_cost = 0.0
    
    async def route_query(self, query: str, context: Dict = None) -> Dict:
        """Route query to appropriate model based on complexity and cost"""
        
        # Step 1: Classify query complexity
        complexity = await self._classify_complexity(query)
        
        # Step 2: Route based on complexity
        if complexity["level"] == "simple":
            result = await self._query_local(query)
            source = "local"
        elif complexity["level"] == "moderate":
            result = await self._query_economy(query)
            source = "cloud_economy"
        else:
            result = await self._query_frontier(query)
            source = "cloud_frontier"
        
        # Step 3: Log cost
        cost = self._calculate_cost(result, source)
        self._log_cost(query, result, cost, source)
        
        return {
            "response": result["text"],
            "source": source,
            "cost": cost,
            "latency_ms": result.get("latency_ms", 0)
        }
    
    async def _classify_complexity(self, query: str) -> Dict:
        """Classify query complexity using lightweight heuristics"""
        # This could be a tiny ML model or simple rules
        word_count = len(query.split())
        has_numbers = any(c.isdigit() for c in query)
        has_specialized_terms = any(
            term in query.lower() 
            for term in ["quantum", "medical", "legal", "code", "algorithm"]
        )
        
        if word_count < 20 and not has_specialized_terms:
            return {"level": "simple", "confidence": 0.9}
        elif word_count < 50 and not has_numbers:
            return {"level": "moderate", "confidence": 0.8}
        else:
            return {"level": "complex", "confidence": 0.7}
    
    async def _query_local(self, query: str) -> Dict:
        """Query local 1-bit model"""
        start = datetime.now()
        result = self.local.generate(query, max_tokens=500)
        latency = (datetime.now() - start).total_seconds() * 1000
        
        return {
            "text": result["text"],
            "latency_ms": latency,
            "input_tokens": len(query.split()),
            "output_tokens": len(result["text"].split())
        }
    
    async def _query_economy(self, query: str) -> Dict:
        """Query cost-effective cloud model"""
        start = datetime.now()
        response = await self.economy.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[{"role": "user", "content": query}],
            max_tokens=1000
        )
        latency = (datetime.now() - start).total_seconds() * 1000
        
        return {
            "text": response.choices[0].message.content,
            "latency_ms": latency,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens
        }
    
    async def _query_frontier(self, query: str) -> Dict:
        """Query frontier model for complex tasks"""
        start = datetime.now()
        response = await self.frontier.messages.create(
            model="claude-opus-4.8",
            max_tokens=2000,
            messages=[{"role": "user", "content": query}]
        )
        latency = (datetime.now() - start).total_seconds() * 1000
        
        return {
            "text": response.content[0].text,
            "latency_ms": latency,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    
    def _calculate_cost(self, result: Dict, source: str) -> float:
        """Calculate cost based on source and token usage"""
        rates = {
            "local": {"input": 0.0001, "output": 0.0001},  # Per 1K tokens
            "cloud_economy": {"input": 0.0005, "output": 0.002},
            "cloud_frontier": {"input": 0.015, "output": 0.075}
        }
        
        rate = rates[source]
        input_cost = (result["input_tokens"] / 1000) * rate["input"]
        output_cost = (result["output_tokens"] / 1000) * rate["output"]
        
        return input_cost + output_cost
    
    def _log_cost(self, query: str, result: Dict, cost: float, source: str):
        """Log query cost for analysis"""
        entry = QueryCost(
            model=source,
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            cost=cost,
            latency_ms=result["latency_ms"],
            source=source
        )
        self.cost_log.append(entry)
        self.total_cost += cost
    
    def get_cost_report(self) -> Dict:
        """Generate cost report"""
        by_source = {}
        for entry in self.cost_log:
            if entry.source not in by_source:
                by_source[entry.source] = {
                    "count": 0,
                    "total_cost": 0.0,
                    "total_latency": 0.0
                }
            by_source[entry.source]["count"] += 1
```python
            by_source[entry.source]["total_cost"] += entry.cost
            by_source[entry.source]["total_latency"] += entry.latency_ms

        report = {
            "total_queries": len(self.cost_log),
            "total_cost": self.total_cost,
            "average_cost_per_query": self.total_cost / len(self.cost_log) if self.cost_log else 0,
            "by_source": by_source,
            "cost_savings": self._calculate_savings()
        }
        return report

    def _calculate_savings(self) -> Dict:
        """Calculate cost savings vs. using only frontier model"""
        if not self.cost_log:
            return {"savings": 0.0, "percentage": 0.0}

        # Simulate cost if all queries went to frontier
        total_frontier_cost = 0.0
        for entry in self.cost_log:
            # Frontier rates
            input_cost = (entry.input_tokens / 1000) * 0.015
            output_cost = (entry.output_tokens / 1000) * 0.075
            total_frontier_cost += input_cost + output_cost

        actual_cost = self.total_cost
        savings = total_frontier_cost - actual_cost
        percentage = (savings / total_frontier_cost) * 100 if total_frontier_cost > 0 else 0

        return {
            "frontier_only_cost": round(total_frontier_cost, 4),
            "actual_cost": round(actual_cost, 4),
            "savings": round(savings, 4),
            "percentage": round(percentage, 2)
        }
