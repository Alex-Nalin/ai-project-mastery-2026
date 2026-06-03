# utils/token_optimizer.py
import tiktoken

def estimate_tokens(text: str, model: str = "gpt-5.5") -> int:
    """Estimate token count for a given text."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # Fallback: rough estimate
        return int(len(text.split()) * 1.3)

def compress_prompt(prompt: str, max_tokens: int = 4000) -> str:
    """Compress a prompt to fit within token limits."""
    current_tokens = estimate_tokens(prompt)
    if current_tokens <= max_tokens:
        return prompt
    
    # Remove redundant whitespace
    compressed = ' '.join(prompt.split())
    
    # Remove repeated instructions
    lines = compressed.split('\n')
    seen = set()
    unique_lines = []
    for line in lines:
        normalized = line.strip().lower()
        if normalized not in seen:
            seen.add(normalized)
            unique_lines.append(line)
    
    return '\n'.join(unique_lines)
