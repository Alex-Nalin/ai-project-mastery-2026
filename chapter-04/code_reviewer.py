# app/ai/code_reviewer.py
import os
from typing import Optional
from openai import AsyncOpenAI
from pydantic import BaseModel, Field


class CodeReviewRequest(BaseModel):
    """Request for AI code review."""
    diff: str = Field(..., description="The git diff to review")
    repository: str = Field(..., description="Repository name")
    pr_number: int = Field(..., description="PR number")
    conventions: Optional[str] = Field(default=None, description="Project coding conventions")


class CodeIssue(BaseModel):
    """A single issue found during code review."""
    file: str
    line: int
    severity: str  # critical, major, minor, suggestion
    category: str  # bug, security, performance, style, architecture, testing
    description: str
    suggestion: str


class CodeReviewResult(BaseModel):
    """Complete code review result."""
    summary: str
    issues: list[CodeIssue]
    positive_feedback: list[str]
    should_approve: bool


class CodeReviewer:
    """Reviews code using GPT-5.5 Pro mode."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(
            api_key=api_key or os.environ["OPENAI_API_KEY"]
        )

    async def review_pr(self, request: CodeReviewRequest) -> CodeReviewResult:
        """Review a pull request and return structured feedback."""

        system_prompt = """You are an expert code reviewer. Review code diffs and provide structured feedback.

Focus on:
- Logic errors and edge cases
- Security vulnerabilities
- Performance bottlenecks
- Code style and consistency
- Missing error handling
- Test coverage gaps

Be constructive and specific. Provide line-level feedback when possible."""

        user_prompt = f"""Review this pull request diff for repository {request.repository}, PR #{request.pr_number}:

{request.diff}

Project conventions:
{request.conventions or 'No specific conventions provided'}

Provide structured feedback as JSON."""

        response = await self.client.chat.completions.create(
            model="gpt-5.5-thinking-20260415",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        import json
        result = json.loads(response.choices[0].message.content)

        return CodeReviewResult(
            summary=result["summary"],
            issues=[CodeIssue(**issue) for issue in result["issues"]],
            positive_feedback=result["positive_feedback"],
            should_approve=result["should_approve"],
        )
