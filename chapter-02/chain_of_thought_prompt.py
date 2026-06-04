import ollama

def chain_of_thought_prompt(question: str) -> str:
    """Run chain-of-thought reasoning with local model."""
    response = ollama.chat(
        model="qwen3.5:72b",
        messages=[
            {
                "role": "system",
                "content": "You are a reasoning system. Always think step by step."
            },
            {
                "role": "user",
                "content": f"{question}\n\nLet's work through this step by step."
            }
        ],
        options={
            "temperature": 0.3,
            "num_predict": 2048
        }
    )
    
    return response['message']['content']

# Example
result = chain_of_thought_prompt(
    "If a train leaves Station A at 60 mph and another leaves Station B at 70 mph, "
    "and the stations are 260 miles apart, when will they meet?"
)
print(result)
