async def write_outreach_email(lead: dict, enrichment: dict, score: int) -> str:
    """Write personalized outreach email."""
    prompt = f"""
    Write a personalized sales email for this lead.
    
    Lead Info:
    Name: {lead['name']}
    Title: {lead['job_title']}
    Company: {lead['company']}
    
    Enrichment Data:
    Industry: {enrichment.get('industry', 'Unknown')}
    Company Size: {enrichment.get('company_size', 'Unknown')}
    Technologies: {', '.join(enrichment.get('technologies_used', []))}
    
    Lead Score: {score}/100
    
    Guidelines:
    - Reference their specific industry or technology stack
    - Address their likely pain points based on role
    - Keep it under 150 words
    - Include a specific call to action
    - Don't sound like a template
    """
    
    # Use Claude Opus 4.8 for better writing quality
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            json={
                "model": "claude-opus-4.8",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300
            },
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            }
        )
        return response.json()['content'][0]['text']
