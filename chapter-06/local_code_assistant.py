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
```

Provide a clear, concise explanation focusing on what the code does and how it works."""
        
        return await self._generate(
            prompt,
            model=self.model_routes["explain"],
            temperature=0.3
        )
    
    async def refactor_code(
        self,
        code: str,
        instructions: str
    ) -> str:
        """Refactor code based on instructions."""
        prompt = f"""Refactor this code according to the instructions:

Code:
```python
{code}
```

Instructions: {instructions}

Provide the complete refactored code."""
        
        return await self._generate(
            prompt,
            model=self.model_routes["refactor"],
            temperature=0.2
        )
    
    async def debug_error(
        self,
        code: str,
        error_message: str
    ) -> str:
        """Debug an error."""
        prompt = f"""Debug this error:

Code:
```python
{code}
```

Error:
{error_message}

Explain the cause and provide the fix."""
        
        return await self._generate(
            prompt,
            model=self.model_routes["debug"],
            temperature=0.2
        )
    
    async def _generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 1024
    ) -> str:
        """Generate text using Ollama."""
        response = await self.client.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
        )
        response.raise_for_status()
        
        # Handle streaming response
        full_text = ""
        for line in response.text.strip().split('\n'):
            if line:
                data = json.loads(line)
                if "response" in data:
                    full_text += data["response"]
        
        return full_text
    
    async def close(self):
        await self.client.aclose()

async def main():
    assistant = LocalCodeAssistant()
    
    # Complete code
    context = """
def calculate_metrics(data):
    total = sum(data)
    count = len(data)
    <CURSOR>
"""
    completion = await assistant.complete_code(context)
    print(f"Completion: {completion}")
    
    # Debug error
    code = """
def divide(a, b):
    return a / b
"""
    error = "ZeroDivisionError: division by zero"
    fix = await assistant.debug_error(code, error)
    print(f"Debug: {fix}")
    
    await assistant.close()
