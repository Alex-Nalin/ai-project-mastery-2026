async def research_topic(topic: str) -> dict:
    """Research a topic using Perplexity API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.perplexity.ai/search",
            json={
                "query": f"Latest developments in {topic} 2026",
                "max_results": 5
            },
            headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}"}
        )
        return response.json()
