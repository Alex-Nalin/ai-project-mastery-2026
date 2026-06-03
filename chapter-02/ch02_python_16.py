from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer

class DynamicFewShotSelector:
    def __init__(self, examples: List[Dict]):
        self.examples = examples
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.example_embeddings = self._encode_examples()
    
    def _encode_examples(self) -> np.ndarray:
        texts = [ex["content"] for ex in self.examples if ex["role"] == "user"]
        return self.encoder.encode(texts)
    
    def select_examples(self, query: str, n: int = 3) -> List[Dict]:
        query_embedding = self.encoder.encode([query])
        similarities = np.dot(self.example_embeddings, query_embedding.T).flatten()
        top_indices = np.argsort(similarities)[-n:][::-1]
        
        # Return both user and assistant messages for selected examples
        selected = []
        for idx in top_indices:
            # Find the pair (user + assistant)
            user_idx = idx * 2  # Assuming alternating user/assistant
            if user_idx < len(self.examples):
                selected.append(self.examples[user_idx])
                if user_idx + 1 < len(self.examples):
                    selected.append(self.examples[user_idx + 1])
        
        return selected

# Usage
selector = DynamicFewShotSelector(FEW_SHOT_EXAMPLES)
query = "Calculate the LTV of a customer who pays $49/month with 3% monthly churn"
relevant_examples = selector.select_examples(query, n=2)
