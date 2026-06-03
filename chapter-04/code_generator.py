# app/ai/code_generator.py
import os
from typing import Optional
from anthropic import AsyncAnthropic
from pydantic import BaseModel, Field


class CodeGenerationRequest(BaseModel):
    """Request for AI code generation."""
    description: str = Field(..., description="Natural language description of the code to generate")
    language: str = Field(default="python", description="Programming language")
    framework: Optional[str] = Field(default=None, description="Framework to use (e.g., FastAPI, React)")
    context: Optional[str] = Field(default=None, description="Additional context or existing code patterns")
    test_framework: Optional[str] = Field(default="pytest", description="Testing framework to use")
    
    model_config = {"frozen": True}


class GeneratedCode(BaseModel):
    """Response containing generated code."""
    code: str = Field(..., description="The generated source code")
    explanation: str = Field(..., description="Explanation of what the code does")
    test_code: Optional[str] = Field(default=None, description="Generated test code")
    warnings: list[str] = Field(default_factory=list, description="Warnings about potential issues")


class CodeGenerator:
    """Generates production-quality code using Claude Opus 4.8."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncAnthropic(
            api_key=api_key or os.environ["ANTHROPIC_API_KEY"]
        )
    
    async def generate_code(
        self,
        request: CodeGenerationRequest,
    ) -> GeneratedCode:
        """Generate code based on a natural language description."""
        
        system_prompt = """You are

an expert software engineer specializing in writing production-quality code.

Rules:
1. Write complete, runnable code with proper error handling
2. Include comprehensive type hints
3. Follow PEP 8 and language-specific best practices
4. Write async code where appropriate
5. Include logging and observability
6. Handle edge cases and error states
7. Use dependency injection for testability
8. Include docstrings for all public functions and classes

Respond with valid JSON containing:
- code: The complete source code
- explanation: What the code does and why you made key decisions
- test_code: pytest tests covering the main functionality
- warnings: Any potential issues or assumptions"""

        user_prompt = f"""Generate {request.language} code for the following description:

{request.description}

Framework: {request.framework or 'None specified'}
Testing: {request.test_framework}

Context:
{request.context or 'No additional context provided'}

Generate production-quality code that handles edge cases and includes proper error handling."""

        response = await self.client.messages.create(
            model="claude-opus-4-8-20260415",
            max_tokens=4000,
            temperature=0.3,  # Lower temperature for more deterministic code
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        # Parse the JSON response
        import json
        result = json.loads(response.content[0].text)

        return GeneratedCode(
            code=result["code"],
            explanation=result["explanation"],
            test_code=result.get("test_code"),
            warnings=result.get("warnings", []),
        )
