def truncate_for_llm(text: str, max_tokens: int = 4000) -> str:
    """Truncate text to fit within token limits (rough estimate: 4 chars per token)."""
    max_chars = max_tokens * 4
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[Content truncated due to length...]"
    return text
