import httpx
import asyncio
from typing import Dict, Any
from pydantic import BaseModel, EmailStr

class LeadData(BaseModel):
    name: str
    email: EmailStr
    company: str
    job_title: str
    source: str
    message: str

async def trigger_lead_workflow(lead: LeadData) -> Dict[str, Any]:
    webhook_url = "https://your-n8n-instance.com/webhook/lead-qualification"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            webhook_url,
            json=lead.model_dump(),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

async def main():
    lead = LeadData(
        name="Sarah Chen",
        email="sarah@techstartup.io",
        company="TechStartup Inc.",
        job_title="CTO",
        source="website_contact_form",
        message="Interested in your enterprise AI automation platform for our data pipeline"
    )
    
    result = await trigger_lead_workflow(lead)
    print(f"Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
