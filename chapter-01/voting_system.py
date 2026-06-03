# advanced/voting_system.py
from typing import List, Dict, Any
from collections import Counter
import json

class MultiModelVoter:
    """Use multiple models to vote on the correct answer."""
    
    def __init__(self, models: list):
        self.models = models
    
    async def vote(
        self, 
        prompt: str,
        num_attempts: int = 3,
        confidence_threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Run multiple models and let them vote."""
        
        all_responses = []
        
        # Run each model multiple times
        for model in self.models:
            for _ in range(num_attempts):
                response = await model.generate(
                    prompt + "\n\nProvide only the answer, no explanation.",
                    temperature=0.3  # Lower temperature for consistency
                )
                if response.content.strip():
                    all_responses.append({
                        'model': model.model_name,
                        'answer': response.content.strip(),
                        'cost': response.cost_usd
                    })
        
        # Count votes
        answers = [r['answer'] for r in all_responses]
        vote_counts = Counter(answers)
        most_common = vote_counts.most_common(1)
        
        if not most_common:
            return {'error': 'No valid responses'}
        
        winner, votes = most_common[0]
        total_votes = len(all_responses)
        confidence = votes / total_votes
        
        return {
            'winner': winner,
            'confidence': confidence,
            'votes': votes,
            'total_votes': total_votes,
            'all_responses': all_responses,
            'total_cost': sum(r['cost'] for r in all_responses)
        }
