async def list_models(self) -> List[Dict]:
    """List available models."""
    response = await self.client.get(f"{self.base_url}/api/tags")
    return response.json()["models"]

async def pull_model(self, model_name: str) -> bool:
    """Pull a model from the registry."""
    response = await self.client.post(
        f"{self.base_url}/api/pull",
        json={"name": model_name}
    )
    return response.status_code == 200
