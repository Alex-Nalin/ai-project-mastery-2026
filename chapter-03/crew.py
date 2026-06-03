# research_crew/crew.py
from crewai import Crew, Process
from .agents import researcher, analyst, writer
from .tasks import research_task, analysis_task, writing_task
import os
from dotenv import load_dotenv

load_dotenv()

research_crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.sequential,  # Tasks execute in order
    verbose=True,
    memory=True,  # Enable short-term memory within the crew
    cache=True,  # Cache tool outputs to avoid redundant API calls
    max_rpm=50,  # Global rate limit
    share_crew=True  # Allow agents to see each other's outputs
)

def run_research(topic: str) -> str:
    """Execute the research crew on a given topic."""
    result = research_crew.kickoff(inputs={"topic": topic})
    return result.raw_output
