# run.py (production version)
import sys
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('research_crew.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# Validate required keys
required_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY']
missing_keys = [key for key in required_keys if not os.getenv(key)]
if missing_keys:
    logger.error(f"Missing required environment variables: {', '.join(missing_keys)}")
    logger.error("Please check your .env file")
    sys.exit(1)

from crew import generate_report

def main():
    topics = [
        "The impact of 1-bit LLMs on edge AI deployment in 2026",
        "Multi-agent systems vs monolithic LLMs: Which approach wins for enterprise?",
        "The rise of neuro-symbolic AI: Combining neural networks with symbolic reasoning"
    ]
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'#'*60}")
        print(f"Report {i}/{len(topics)}: {topic}")
        print(f"{'#'*60}\n")
        
        try:
            report = generate_report(topic)
            print(f"\n✓ Report completed successfully")
            print(f"  Length: {len(report)} characters")
            print(f"  Preview: {report[:200]}...\n")
        except Exception as e:
            logger.error(f"Failed to generate report for '{topic}': {str(e)}")
            # Continue with next topic instead of failing entirely
            continue

if __name__ == "__main__":
    main()
