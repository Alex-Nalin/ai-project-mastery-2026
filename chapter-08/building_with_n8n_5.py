async def

```python
async def create_hubspot_contact(lead: dict, enrichment: dict, score: int, outreach_email: str) -> dict:
    """Create or update contact in HubSpot with AI-generated data."""
    async with httpx.AsyncClient() as client:
        # First, check if contact exists
        search_response = await client.post(
            "https://api.hubapi.com/crm/v3/objects/contacts/search",
            json={
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": lead['email']
                    }]
                }]
            },
            headers={"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
        )
        
        existing_contacts = search_response.json().get('results', [])
        
        contact_data = {
            "properties": {
                "email": lead['email'],
                "firstname": lead['name'].split()[0],
                "lastname": ' '.join(lead['name'].split()[1:]),
                "jobtitle": lead['job_title'],
                "company": lead['company'],
                "hs_lead_status": "NEW",
                "ai_lead_score": score,
                "ai_qualification": "hot" if score > 70 else "warm" if score > 40 else "cold",
                "ai_outreach_email": outreach_email,
                "enriched_industry": enrichment.get('industry', ''),
                "enriched_company_size": str(enrichment.get('company_size', '')),
                "enriched_technologies": ', '.join(enrichment.get('technologies_used', [])),
                "enriched_funding": enrichment.get('funding', ''),
                "lead_source": "website_form_ai_qualified"
            }
        }
        
        if existing_contacts:
            # Update existing contact
            contact_id = existing_contacts[0]['id']
            response = await client.patch(
                f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}",
                json=contact_data,
                headers={"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
            )
        else:
            # Create new contact
            response = await client.post(
                "https://api.hubapi.com/crm/v3/objects/contacts",
                json=contact_data,
                headers={"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
            )
        
        return response.json()
