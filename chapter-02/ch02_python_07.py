from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
import json

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative" 
    NEUTRAL = "neutral"
    MIXED = "mixed"

class Entity(BaseModel):
    name: str = Field(description="The entity name")
    type: str = Field(description="Entity type: person, organization, location, product")
    sentiment: Sentiment = Field(description="Sentiment toward this entity")
    mentions: int = Field(ge=1, description="Number of mentions in the text")
    
    @field_validator('type')
    def validate_type(cls, v):
        valid_types = ['person', 'organization', 'location', 'product', 'event']
        if v.lower() not in valid_types:
            raise ValueError(f'Type must be one of {valid_types}')
        return v.lower()

class AnalysisResult(BaseModel):
    summary: str = Field(description="One-sentence summary of the text")
    entities: List[Entity] = Field(description="Extracted entities")
    overall_sentiment: Sentiment = Field(description="Overall sentiment")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    key_topics: List[str] = Field(description="Key topics discussed")

# Usage with GPT-5.5
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

response = client.chat.completions.create(
    model="gpt-5.5-2026-04-01",
    messages=[
        {
            "role": "system",
            "content": "You are an analysis system. Always return valid JSON matching the required schema."
        },
        {
            "role": "user",
            "content": "Analyze this text: 'Apple announced a new partnership with Microsoft to develop AI tools for healthcare. The collaboration was praised by industry experts but raised privacy concerns among consumer advocates.'"
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "analysis_result",
            "schema": AnalysisResult.model_json_schema()
        }
    }
)

# Parse and validate
result = AnalysisResult.model_validate_json(
    response.choices[0].message.content
)
print(f"Summary: {result.summary}")
print(f"Entities: {[e.name for e in result.entities]}")
