# decision_engine.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

class TaskType(Enum):
    TEXT_GENERATION = "text_generation"
    CODING = "coding"
    MULTIMODAL = "multimodal"
    REASONING = "reasoning"
    AGENTIC = "agentic"
    ANALYSIS = "analysis"

class CostTier(Enum):
    LOW = "low"      # < $0.01 per query
    MEDIUM = "medium" # $0.01 - $0.10 per query
    HIGH = "high"     # > $0.10 per query

@dataclass
class TaskRequirements:
    task_type: TaskType
    cost_tier: CostTier
    min_context_tokens: int
    needs_real_time_data: bool
    needs_multimodal: bool
    latency_sensitive: bool
    privacy_required: bool

@dataclass
class ModelRecommendation:
    primary_model: str
    fallback_model: str
    estimated_cost_per_query: float
    estimated_latency_ms: float
    confidence_score: float
    reasoning: str

class ModelDecisionEngine:
    """Intelligently routes tasks to the optimal model."""
    
    def __init__(self):
        self.model_profiles = {
            "claude-mythos-5": {
                "strengths": [TaskType.REASONING, TaskType.ANALYSIS],
                "cost_per_1k_tokens": 0.075,
                "max_context": 200000,
                "avg_latency_ms": 8000,
                "supports_real_time": False,
                "supports_multimodal": False,
                "privacy_rating": 5
            },
            "gpt-5.5": {
                "strengths": [TaskType.TEXT_GENERATION, TaskType.CODING],
                "cost_per_1k_tokens": 0.030,
                "max_context": 128000,
                "avg_latency_ms": 3000,
                "supports_real_time": False,
                "supports_multimodal": False,
                "privacy_rating": 3
            },
            "gpt-5.5-thinking": {
                "strengths": [TaskType.REASONING, TaskType.ANALYSIS, TaskType.CODING],
                "cost_per_1k_tokens": 0.100,
                "max_context": 128000,
                "avg_latency_ms": 12000,
                "supports_real_time": False,
                "supports_multimodal": False,
                "privacy_rating": 3
            },
            "gemini-3.5-pro": {
                "strengths": [TaskType.MULTIMODAL, TaskType.ANALYSIS, TaskType.TEXT_GENERATION],
                "cost_per_1k_tokens": 0.025,
                "max_context": 1000000,
                "avg_latency_ms": 2000,
                "supports_real_time": False,
                "supports_multimodal": True,
                "privacy_rating": 3
            },
            "claude-opus-4-8": {
                "strengths": [TaskType.REASONING, TaskType.AGENTIC, TaskType.CODING],
                "cost_per_1k_tokens": 0.050,
                "max_context": 200000,
                "avg_latency_ms": 6000,
                "supports_real_time": False,
                "supports_multimodal": False,
                "privacy_rating": 5
            },
            "grok-4.20": {
                "strengths": [TaskType.AGENTIC, TaskType.ANALYSIS],
                "cost_per_1k_tokens": 0.040,
                "max_context": 128000,
                "avg_latency_ms": 5000,
                "supports_real_time": True,
                "supports_multimodal": False,
                "privacy_rating": 2
            },
            "deepseek-v4-pro": {
                "strengths": [TaskType.TEXT_GENERATION, TaskType.CODING, TaskType.ANALYSIS],
                "cost_per_1k_tokens": 0.003,
                "max_context": 128000,
                "avg_latency_ms": 4000,
                "supports_real_time": False,
                "supports_multimodal": False,
                "privacy_rating": 2
            },
            "qwen-3.5": {
                "strengths": [TaskType.AGENTIC, TaskType.ANALYSIS],
                "cost_per_1k_tokens": 0.002,
                "max_context": 1000000,
                "avg_latency_ms": 5000,
                "supports_real_time": False,
                "supports_multimodal": False,
                "privacy_rating": 4
            },
            "glm-5.1": {
                "strengths": [TaskType.REASONING, TaskType.CODING],
                "cost_per_1k_tokens": 0.002,
                "max_context": 128000,
                "avg_latency_ms": 6000,
                "supports_real_time": False,
                "supports_multimodal": False,
                "privacy_rating": 4
            },
            "gemma-4": {
                "strengths": [TaskType.MULTIMODAL, TaskType.TEXT_GENERATION],
                "cost_per_1k_tokens": 0.001,  # Local, effectively free
                "max_context": 32000,
                "avg_latency_ms": 2000,
                "supports_real_time": False,
                "supports_multimodal": True,
                "privacy_rating": 5  # Runs locally
            }
        }
    
    def recommend(self, requirements: TaskRequirements) -> ModelRecommendation:
        """Recommend the best model for a given task."""
        
        candidates = []
        
        for model_name, profile in self.model_profiles.items():
            score = 0.0
            reasons = []
            
            # Check task type match
            if requirements.task_type in profile["strengths"]:
                score += 3.0
                reasons.append(f"Strong at {requirements.task_type.value}")
            
            # Check context window
            if profile["max_context"] >= requirements.min_context_tokens:
                score += 2.0
            else:
                score -= 5.0  # Deal breaker
                reasons.append(f"Context window too small ({profile['max_context']} < {requirements.min_context_tokens})")
            
            # Check cost
            if requirements.cost_tier == CostTier.LOW:
                if profile["cost_per_1k_tokens"] <= 0.005:
                    score += 2.0
                elif profile["cost_per_1k_tokens"] <= 0.05:
                    score += 1.0
                else:
                    score -= 2.0
                    reasons.append("Too expensive for budget tier")
            
            # Check real-time data needs
            if requirements.needs_real_time_data and not profile["supports_real_time"]:
                score -= 3.0
                reasons.append("Doesn't support real-time data")
            
            # Check multimodal needs
            if requirements.needs_multimodal and not profile["supports_multimodal"]:
                score -= 3.0
                reasons.append("Doesn't support multimodal input")
            
            # Check latency sensitivity
            if requirements.latency_sensitive and profile["avg_latency_ms"] > 5000:
                score -= 2.0
                reasons.append("Too slow for latency-sensitive task")
            
            # Check privacy requirements
            if requirements.privacy_required and profile["privacy_rating"] < 4:
                score -= 3.0
                reasons.append("Privacy rating too low")
            
            candidates.append({
                'model': model_name,
                'score': score,
                'reasons': reasons,
                'profile': profile
            })
        
        # Sort by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        if not candidates:
            return ModelRecommendation(
                primary_model="gpt-5.5",
                fallback_model="claude-opus-4-8",
                estimated_cost_per_query=0.03,
                estimated_latency_ms=3000,
                confidence_score=0.5,
                reasoning="No optimal model found, falling back to defaults"
            )
        
        best = candidates[0]
        fallback = candidates[1] if len(candidates) > 1 else candidates[0]
        
        # Estimate cost based on average query size (1000 tokens)
        estimated_cost = best['profile']['cost_per_1k_tokens']
        
        return ModelRecommendation(
            primary_model=best['model'],
            fallback_model=fallback['model'],
            estimated_cost_per_query=estimated_cost,
            estimated_latency_ms=best['profile']['avg_latency_ms'],
            confidence_score=max(0, min(1.0, best['score'] / 10)),
            reasoning="; ".join(best['reasons']) if best['reasons'] else "Best overall match"
        )

# Example usage
if __name__ == "__main__":
    engine = ModelDecisionEngine()
    
    # Example 1: Budget code generation
    req1 = TaskRequirements(
        task_type=TaskType.CODING,
        cost_tier=CostTier.LOW,
        min_context_tokens=4000,
        needs_real_time_data=False,
        needs_multimodal=False,
        latency_sensitive=True,
        privacy_required=False
    )
    
    rec1 = engine.recommend(req1)
    print(f"Code generation: Use {rec1.primary_model} (${rec1.estimated_cost_per_query:.4f}/query)")
    print(f"  Reason: {rec1.reasoning}")
    
    # Example 2: High-stakes legal analysis
    req2 = TaskRequirements(
        task_type=TaskType.REASONING,
        cost_tier=CostTier.HIGH,
        min_context_tokens=100000,
        needs_real_time_data=False,
        needs_multimodal=False,
        latency_sensitive=False,
        privacy_required=True
    )
    
    rec2 = engine.recommend(req2)
    print(f"Legal analysis: Use {rec2.primary_model} (${rec2.estimated_cost_per_query:.4f}/query)")
    print(f"  Reason: {rec2.reasoning}")
    
    # Example 3: Real-time social media monitoring
    req3 = TaskRequirements(
        task_type=TaskType.ANALYSIS,
        cost_tier=CostTier.MEDIUM,
        min_context_tokens=8000,
        needs_real_time_data=True,
        needs_multimodal=False,
        latency_sensitive=True,
        privacy_required=False
    )
    
    rec3 = engine.recommend(req3)
    print(f"Social monitoring: Use {rec3.primary_model} (${rec3.estimated_cost_per_query:.4f}/query)")
    print(f"  Reason: {rec3.reasoning}")
