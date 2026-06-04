import hashlib
import json
from datetime import datetime

class PromptVersionTracker:
    """Track prompt versions and their performance over time."""
    
    def __init__(self, storage_path: str = "prompt_versions.json"):
        self.storage_path = storage_path
        self.versions = self._load_versions()
    
    def register_prompt(self, workflow_name: str, prompt: str, model: str) -> str:
        """Register a new prompt version and return its hash."""
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:12]
        
        version_entry = {
            "workflow": workflow_name,
            "prompt_hash": prompt_hash,
            "model": model,
            "prompt": prompt,
            "created_at": datetime.utcnow().isoformat(),
            "performance_metrics": {
                "accuracy": None,
                "avg_cost_per_call": None,
                "avg_latency_ms": None,
                "total_calls": 0
            }
        }
        
        if workflow_name not in self.versions:
            self.versions[workflow_name] = []
        
        self.versions[workflow_name].append(version_entry)
        self._save_versions()
        return prompt_hash
    
    def update_metrics(self, workflow_name: str, prompt_hash: str, 
                      accuracy: float, cost: float, latency: float):
        """Update performance metrics for a prompt version."""
        for version in self.versions.get(workflow_name, []):
            if version["prompt_hash"] == prompt_hash:
                metrics = version["performance_metrics"]
                n = metrics["total_calls"]
                # Running average
                metrics["accuracy"] = (metrics["accuracy"] * n + accuracy) / (n + 1) if metrics["accuracy"] else accuracy
                metrics["avg_cost_per_call"] = (metrics["avg_cost_per_call"] * n + cost) / (n + 1) if metrics["avg_cost_per_call"] else cost
                metrics["avg_latency_ms"] = (metrics["avg_latency_ms"] * n + latency) / (n + 1) if metrics["avg_latency_ms"] else latency
                metrics["total_calls"] += 1
                break
        
        self._save_versions()
    
    def get_best_prompt(self, workflow_name: str) -> dict:
        """Get the best performing prompt version for a workflow."""
        versions = self.versions.get(workflow_name, [])
        if not versions:
            return None
        
        # Score each version by accuracy, cost efficiency, and latency
        def score(v):
            m = v["performance_metrics"]
            if m["total_calls"] < 100:  # Not enough data
                return -1
            accuracy_score = m["accuracy"] * 100
            cost_score = max(0, 100 - (m["avg_cost_per_call"] * 10))
            latency_score = max(0, 100 - (m["avg_latency_ms"] / 100))
            return accuracy_score * 0.5 + cost_score * 0.3 + latency_score * 0.2
        
        return max(versions, key=score)
    
    def _load_versions(self) -> dict:
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_versions(self):
        with open(self.storage_path, 'w') as f:
            json.dump(self.versions, f, indent=2)

# Usage
tracker = PromptVersionTracker()

# Register a new prompt
prompt_hash = tracker.register_prompt(
    workflow_name="email_classifier",
    prompt="You are an email classification agent...",
    model="gpt-5.5-thinking"
)

# After processing 1000 emails, update metrics
tracker.update_metrics(
    workflow_name="email_classifier",
    prompt_hash=prompt_hash,
    accuracy=0.94,
    cost=0.0023,
    latency=450
)
