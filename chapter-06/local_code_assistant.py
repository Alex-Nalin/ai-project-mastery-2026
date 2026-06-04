import httpx
from typing import Optional, Dict, List
import json

class LocalCodeAssistant:
    """Bridges Cursor with local Ollama models."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # Model routing rules
        self.model_routes = {
            "chat": "qwen3.5:32b",
            "completion": "phi-4:14b",
            "refactor": "deepseek-v4-pro:67b",
            "explain": "qwen3.5:32b",
            "debug": "deepseek-v4-pro:67b"
        }
    
    async def complete_code(
        self,
        context: str,
        cursor_position: int,
        language: str = "python"
    ) -> str:
        """Generate code completion."""
        prompt = f"""Complete the following {language} code at the cursor position (marked with <CURSOR>):

{context[:cursor_position]}<CURSOR>{context[cursor_position:]}

Provide only the completion, no explanation."""
        
        response = await self._generate(
            prompt,
            model=self.model_routes["completion"],
            temperature=0.1,
            max_tokens=256
        )
        return response
    
    async def explain_code(self, code: str) -> str:
        """Explain what code does."""
        prompt = f"""Explain this code in simple terms:

```python
{code}
