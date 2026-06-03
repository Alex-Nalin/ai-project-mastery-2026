# models/openai_wrapper.py
import time
from typing import Optional
from openai import AsyncOpenAI
from .base import BaseModel, ModelResponse

class OpenAIWrapper(BaseModel):
    def __init__(self, api_key: str, model: str = "gpt-5.5"):
        self.client = AsyncOpenAI(api_key=api_key)
        self._model = model
        
        # Pricing per million tokens (input/output)
        self.pricing = {
            "gpt-5.5": (30.0, 90.0),
            "gpt-5.5-pro": (60.0, 180.0),
            "gpt-5.5-thinking": (100.0, 300.0),
        }
    
    @property
    def model_name(self) -> str:
        return self._model
    
    @property
    def provider(self) -> str:
        return "OpenAI"
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> ModelResponse:
        start_time = time.time()
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            return ModelResponse(
                model_name=self._model,
                content=response.choices[0].message.content,
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                latency_ms=elapsed_ms,
                cost_usd=self.calculate_cost(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
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
            self._model, (30.0, 90.0)
        )
        return (input_tokens * input_price + output_tokens * output_price) / 1_000_000
