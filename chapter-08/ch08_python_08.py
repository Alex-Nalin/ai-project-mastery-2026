from pydantic import BaseModel, EmailStr, validator
from typing import Optional

class WebhookPayload(BaseModel):
    email: EmailStr
    name: str
    company: Optional[str] = None
    message: str
    source: str
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        if len(v) > 5000:
            raise ValueError('Message too long')
        return v.strip()
    
    @validator('name')
    def name_valid(cls, v):
        if len(v) > 100:
            raise ValueError('Name too long')
        return v.strip()
