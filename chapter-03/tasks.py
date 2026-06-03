# research_crew/tasks.py
from crewai import Task
from typing import List

research_task = Task(
    description="""
    Research the following topic thoroughly: {topic}
    
    Your research should cover:
    1. Current state of the topic (latest developments in the last 3 months)
    2. Key players and their positions
    3. Relevant data points, statistics, and trends
    4. Contradictory viewpoints or controversies
    5. Primary sources for all claims
    
    Compile your findings into a structured research brief with citations.
    """,
    expected_output="A comprehensive research brief with at least 10 verified sources, organized by theme",
    agent=researcher,
    async_execution=False  # Research must complete before analysis
)

analysis_task = Task(
    description="""
    Analyze the research brief provided by the Research Analyst on the topic: {topic}
    
    Your analysis should:
    1. Identify the 3-5 most significant trends or insights
    2. Assess the reliability of key claims (high/medium/low confidence)
    3. Identify gaps in the research that need further investigation
    4. Provide strategic recommendations based on the findings
    5. Flag any contradictory information that needs resolution
    
    If you need additional data, delegate back to the Research Analyst.
    """,
    expected_output="A strategic analysis document with confidence ratings and actionable recommendations",
    agent=analyst,
    async_execution=False,
    context=[research_task]  # Depends on research completion
)

writing_task = Task(
    description="""
    Based on the research brief and strategic analysis, write a professional report on: {topic}
    
    The report should:
    1. Begin with an executive summary (max 200 words)
    2. Follow with detailed sections covering key findings
    3. Include data visualizations described in text (since we can't render images)
    4. End with strategic recommendations and next steps
    5. Be written for a C-suite audience - clear, concise, and actionable
    
    Tone: Professional but engaging. Avoid jargon unless defined.
    Length: 1500-2000 words.
    """,
    expected_output="A polished, publication-ready report in markdown format",
    agent=writer,
    async_execution=False,
    context=[research_task, analysis_task]  # Depends on both prior tasks
)
