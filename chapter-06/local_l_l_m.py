import httpx
import json
from typing import List, Dict, Optional

class LocalLLM:
    """A client for Ollama's API."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen3.5:32b"):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> str:
        """Send a chat completion request."""
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": stream
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/chat",
            json=payload
        )
        response.raise_for_status()
        
        if stream:
            return await self._handle_stream(response)
        
        result = response.json()
        return result["message"]["content"]
    
    async def _handle_stream(self, response):
        """Process streaming response."""
        full_content = ""
        async for line in response.aiter_lines():
            if line:
                data = json.loads(line)
                if "message" in data and "content" in data["message"]:
                    full_content += data["message"]["content"]
        return full_content
    
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> str:
        """Simple text generation (non-chat)."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return await self.chat(messages, **kwargs)
    
    async def close(self):
        await self.client.aclose()

# Usage
async def main():
    llm = LocalLLM()
    response = await llm.chat([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantization in 3 sentences."}
    ])
    print(response)
    await llm.close()
