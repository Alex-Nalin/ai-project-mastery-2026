async def get_embedding(self, text: str) -> List[float]:
    """Generate embeddings using Ollama."""
    payload = {
        "model": self.model,  # Must be an embedding-capable model
        "prompt": text
    }
    
    response = await self.client.post(
        f"{self.base_url}/api/embeddings",
        json=payload
    )
    response.raise_for_status()
    return response.json()["embedding"]
