# utils/model_cascade.py
from typing import Optional, Callable, Awaitable

class ModelCascade:
    """Try cheap models first, escalate to expensive ones if needed."""
    
    def __init__(self, models: list):
        self.models = models  # Ordered from cheapest to most expensive
    
    async def execute_with_escalation(
        self,
        prompt: str,
        quality_check: Callable[[str], Awaitable[float]],
        threshold: float = 0.8
    ) -> tuple[str, str, float]:
        """Execute prompt through models, escalating if quality is low."""
        
        for model in self.models:
            response = await model.generate(prompt)
            if response.error:
                continue
            
            quality_score = await quality_check(response.content)
            
            if quality_score >= threshold:
                return response.content, model.model_name, quality_score
            
            print(f"Quality too low ({quality_score:.2f}) for {model.model_name}, escalating...")
        
        # If all models fail, return the best we got
        return response.content, model.model_name, quality_score
