# main.py
import asyncio
import os
from dotenv import load_dotenv
from comparator import ModelComparator

load_dotenv()

async def main():
    # Load API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    if not all([openai_key, anthropic_key, google_key]):
        print("Error: Missing API keys. Check your .env file.")
        return
    
    # Initialize comparator
    comparator = ModelComparator(openai_key, anthropic_key, google_key)
    
    # Test prompts
    test_prompts = [
        "Explain the concept of quantum entanglement in simple terms.",
        "Write a Python function that implements a binary search tree.",
        "What are the key differences between REST and GraphQL APIs?",
        "Create a business plan outline for a SaaS startup.",
        "Analyze the pros and cons of using microservices architecture."
    ]
    
    print("Running model comparison...")
    print("=" * 60)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}/{len(test_prompts)}")
        result = await comparator.compare(prompt)
        comparator.display_results(result)
    
    print("\nComparison complete!")

if __name__ == "__main__":
    asyncio.run(main())
