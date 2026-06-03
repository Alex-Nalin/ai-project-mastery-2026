# crew.py (enhanced version)
from crewai import Crew, Process
from .agents import researcher, analyst, writer, fact_checker
from .tasks import research_task, analysis_task, fact_check_task, writing_task
import os
from datetime import datetime

research_crew = Crew(
    agents=[researcher, analyst, fact_checker, writer],
    tasks=[research_task, analysis_task, fact_check_task, writing_task],
    process=Process.sequential,
    verbose=True,
    memory=True,
    cache=True,
    max_rpm=50,
    share_crew=True,
    output_log_file=f"logs/crew_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

def generate_report(topic: str, save_to_file: bool = True) -> str:
    """Generate a comprehensive research report on any topic.
    
    Args:
        topic: The research topic/question
        save_to_file: Whether to save the report to a file
        
    Returns:
        The complete report text
    """
    print(f"\n{'='*60}")
    print(f"Starting research on: {topic}")
    print(f"{'='*60}\n")
    
    result = research_crew.kickoff(inputs={"topic": topic})
    report = result.raw_output
    
    if save_to_file:
        filename = f"reports/{topic.replace(' ', '_')[:50]}_{datetime.now().strftime('%Y%m%d')}.md"
        os.makedirs("reports", exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {filename}")
    
    return report
