# models/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ModelResponse:
    model_name: str
    content: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    error: Optional[str] = None

class BaseModel(ABC):
    """Abstract base class for all AI model wrappers."""
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> ModelResponse:
        """Send a prompt to the model and return the response."""
        pass
    
    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate the cost of a request based on token usage."""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the human-readable model name."""
        pass
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """Return the provider name (e.g., 'OpenAI', 'Anthropic')."""
        pass
