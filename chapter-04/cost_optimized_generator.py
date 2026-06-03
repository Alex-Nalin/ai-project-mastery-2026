# app/ai/cost_optimized_generator.py
import hashlib
import json
from typing import Optional
from functools import lru_cache
from app.ai.code_generator import CodeGenerator, CodeGenerationRequest, GeneratedCode


class CostOptimizedGenerator:
    """Wraps code generation with caching and model selection."""

    def __init__(self):
        self.premium_generator = CodeGenerator()  # Claude Opus 4.8
        self.cache: dict[str, GeneratedCode] = {}

    def _get_cache_key(self, request: CodeGenerationRequest) -> str:
        """Generate a cache key from the request."""
        content = f"{request.description}|{request.language}|{request.framework}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def generate_code(
        self,
        request: CodeGenerationRequest,
        use_premium: bool = False,
    ) -> GeneratedCode:
        """Generate code with automatic caching and model selection."""

        # Check cache first
        cache_key = self._get_cache_key(request)
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Use cheaper model for simple tasks
        if not use_premium and self._is_simple_task(request):
            # Use Qwen 3.6 for simple boilerplate
            return await self._generate_with_qwen(request)

        # Use premium model for complex tasks
        result = await self.premium_generator.generate_code(request)

        # Cache the result
        self.cache[cache_key] = result

        return result

    def _is_simple_task(self, request: CodeGenerationRequest) -> bool:
        """Determine if a task is simple enough for a cheaper model."""
        simple_keywords = [
            "boilerplate", "scaffold", "template", "skeleton",
            "crud", "basic", "simple", "standard",
        ]
        description_lower = request.description.lower()
        return any(keyword in description_lower for keyword in simple_keywords)

    async def _generate_with_qwen(self, request: CodeGenerationRequest) -> GeneratedCode:
        """Generate code using Qwen 3.6 for cost efficiency."""
        # Implementation using Qwen 3.6 API
        # Similar to CodeGenerator but with cheaper model
        pass
