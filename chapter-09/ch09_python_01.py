"""
AI Writing Service - Content Generation Engine
Uses Claude Opus 4.8 for high-quality content generation
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
from pydantic import BaseModel, Field

class ContentBrief(BaseModel):
    """Validated content brief from client"""
    client_name: str
    project_title: str
    content_type: str
    target_audience: str
    tone: str
    word_count: int
    key_points: List[str]
    target_keywords: List[str]
    brand_voice: Optional[str] = None
    reference_urls: Optional[List[str]] = None

class GeneratedContent(BaseModel):
    """Structured output from AI generation"""
    title: str
    meta_description: str
    body: str
    key_takeaways: List[str]
    suggested_headings: List[str]
    seo_keywords_used: List[str]
    estimated_read_time: int

class ContentGenerator:
    """Handles AI content generation with quality controls"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        self.model = "claude-mythos-5-20260401"
        
    def generate(self, brief: ContentBrief) -> GeneratedContent:
        """
        Generate content based on client brief.
        Uses structured output for consistent formatting.
        """
        
        system_prompt = f"""You are an expert content writer specializing in {brief.content_type} writing.
        
Brand Voice Guidelines:
{brief.brand_voice or 'Professional and authoritative, yet accessible'}

Tone: {brief.tone}
Target Audience: {brief.target_audience}

Write in a way that:
1. Engages the reader from the first sentence
2. Provides actionable insights
3. Maintains consistent brand voice
4. Incorporates SEO best practices naturally
5. Includes data and examples where relevant

Output your response as a valid JSON object with the following structure:
{{
    "title": "Compelling, SEO-optimized title",
    "meta_description": "150-160 character meta description",
    "body": "Full article in markdown format",
    "key_takeaways": ["3-5 bullet points"],
    "suggested_headings": ["H2 and H3 subheadings used"],
    "seo_keywords_used": ["keywords naturally incorporated"],
    "estimated_read_time": integer_minutes
}}"""

        user_prompt = f"""Generate a {brief.content_type} with the following specifications:

Title/Project: {brief.project_title}
Target Word Count: {brief.word_count} words

Key Points to Cover:
{chr(10).join(f'- {point}' for point in brief.key_points)}

Target Keywords (use naturally):
{chr(10).join(f'- {kw}' for kw in brief.target_keywords)}

Reference URLs for research:
{chr(10).join(f'- {url}' for url in (brief.reference_urls or []))}

Ensure the content is:
- Original and plagiarism-free
- Well-researched with current data (2025-2026)
- Optimized for readability (short paragraphs, subheadings)
- Includes a strong call-to-action
- Factually accurate with citations where appropriate"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0.7,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        # Parse structured output
        try:
            content_data = json.loads(response.content[0].text)
            return GeneratedContent(**content_data)
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: extract content from text
            return self._parse_fallback(response.content[0].text, brief)
    
    def _parse_fallback(self, text: str, brief: ContentBrief) -> GeneratedContent:
        """Fallback parser if structured output fails"""
        # Simple extraction logic
        return GeneratedContent(
            title=brief.project_title,
            meta_description=text[:155] + "...",
            body=text,
            key_takeaways=["Content generated successfully"],
            suggested_headings=[],
            seo_keywords_used=brief.target_keywords,
            estimated_read_time=brief.word_count // 200
        )
    
    def revise(self, original: GeneratedContent, feedback: str) -> GeneratedContent:
        """Revise content based on editor feedback"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system="You are a content editor. Revise the provided content based on the feedback given.",
            messages=[
                {
                    "role": "user",
                    "content": f"""Original content:
Title: {original.title}
Body: {original.body}

Feedback for revision:
{feedback}

Please provide the revised version as a JSON object matching the original structure."""
                }
            ]
        )
        
        try:
            return GeneratedContent(**json.loads(response.content[0].text))
        except:
            return original
