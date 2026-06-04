# In app.py, add webhook for lead capture
import requests

def capture_lead(email: str, analysis_type: str, usage_count: int):
    """Send lead data to your CRM or email list"""
    
    webhook_url = os.getenv("LEAD_WEBHOOK_URL")
    if not webhook_url:
        return
    
    payload = {
        "email": email,
        "source": "huggingface_demo",
        "analysis_type": analysis_type,
        "usage_count": usage_count,
        "timestamp": datetime.now().isoformat(),
        "conversion_point": "free_tier_exhausted"
    }
    
    try:
        requests.post(webhook_url, json=payload, timeout=5)
    except:
        pass  # Don't break the demo if webhook fails
