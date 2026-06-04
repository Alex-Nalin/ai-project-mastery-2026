async def enrich_lead(email: str, company: str) -> dict:
    """Enrich lead data using Clay API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.clay.com/v3/enrich",
            json={
                "email": email,
                "company": company,
                "include": [
                    "linkedin_url",
                    "company_size",
                    "industry",
                    "funding",
                    "technologies_used",
                    "recent_news"
                ]
            },
            headers={"Authorization": f"Bearer {CLAY_API_KEY}"}
        )
        return response.json()
