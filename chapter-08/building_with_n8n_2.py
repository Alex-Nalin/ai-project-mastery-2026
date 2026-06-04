async def score_lead(lead_data: dict) -> dict:
    """Score a lead using GPT-5.5 Pro."""
    prompt = f"""
    Score this lead on a scale of 0-100 based on:
    - Budget indicators (mentions of budget, pricing, investment)
    - Authority (job title suggests decision-making power)
    - Need (clear problem that matches our solution)
    - Timeline (urgency in their message)
    
    Lead Data:
    Name: {lead_data['name']}
    Title: {lead_data['job_title']}
    Company: {lead_data['company']}
    Message: {lead_data['message']}
    
    Return JSON:
    {{
        "score": 0-100,
        "budget_score": 0-10,
        "authority_score": 0-10,
        "need_score": 0-10,
        "timeline_score": 0-10,
        "qualification": "hot|warm|cold",
        "reasoning": "brief explanation"
    }}
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-5.5-thinking",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            },
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
        )
        return response.json()['choices'][0]['message']['content']
