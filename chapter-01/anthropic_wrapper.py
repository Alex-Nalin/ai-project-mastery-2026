# models/anthropic_wrapper.py
import time
from typing import Optional
from anthropic import AsyncAnthropic
from .base import BaseModel, ModelResponse

class AnthropicWrapper(BaseModel):
    def __init__(self, api_key: str, model: str = "claude-opus-4-8"):
        self.client = AsyncAnthropic(api_key=api_key)
        self._model = model
        
        self.pricing = {
            "claude-opus-4-8": (50.0, 150.0),
            "claude-mythos-5": (75.0, 300.0),
        }
    
    @property
    def model_name(self) -> str:
        return self._model
    
    @property
    def provider(self) -> str:
        return "Anthropic"
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> ModelResponse:
        start_time = time.time()
        
        try:
            response = await self.client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            return ModelResponse(
                model_name=self._model,
                content=response.content[0].text,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                latency_ms=elapsed_ms,
                cost_usd=self.calculate_cost(
                    response.usage.input_tokens,
                    response.usage.output_tokens
                )
            )
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            return ModelResponse(
                model_name=self._model,
                content="",
                input_tokens=0,
                output_tokens=0,
                latency_ms=elapsed_ms,
                cost_usd=0.0,
                error=str(e)
            )
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        input_price, output_price = self.pricing.get(
            self._model, (50.0, 150.0)
        )
        return (input_tokens * input_price + output_tokens * output_price) / 1_000_000
