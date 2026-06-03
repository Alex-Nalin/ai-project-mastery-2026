# run_research.py
from research_crew.crew import run_research

report = run_research("The impact of 1-bit LLMs on edge AI deployment in 2026")
print(report[:500])  # Preview first 500 characters
