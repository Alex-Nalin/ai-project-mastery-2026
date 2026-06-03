# models/google_wrapper.py
import time
from typing import Optional
import google.generativeai as genai
from .base import BaseModel, ModelResponse

class GoogleWrapper(BaseModel):
    def __init__(self, api_key: str, model: str = "gemini-3.5-pro"):
        genai.configure(api_key=api_key)
        self._model = model
        self.client = genai.GenerativeModel(model)
        
        self.pricing = {
            "gemini-3.5-pro": (25.0, 75.0),
            "gemini-3.5-ultra": (50.0, 150.0),
        }
    
    @property
    def model_name(self) -> str:
        return self._model
    
    @property
    def provider(self) -> str:
        return "Google"
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> ModelResponse:
        start_time = time.time()
        
        try:
            # Gemini uses system instructions differently
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )
            
            if system_prompt:
                self.client = genai.GenerativeModel(
                    self._model,
                    system_instruction=system_prompt
                )
            
            response = await self.client.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Gemini's token counting is approximate
            input_tokens = len(prompt.split()) * 1.3  # rough estimate
            output_tokens = len(response.text.split()) * 1.3
            
            return ModelResponse(
                model_name=self._model,
                content=response.text,
                input_tokens=int(input_tokens),
                output_tokens=int(output_tokens),
                latency_ms=elapsed_ms,
                cost_usd=self.calculate_cost(
                    int(input_tokens),
                    int(output_tokens)
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
            self._model, (25.0, 75.0)
        )
        return (input_tokens * input_price + output_tokens * output_price) / 1_000_000
