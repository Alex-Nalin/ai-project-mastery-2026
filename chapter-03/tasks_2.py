# tasks.py (enhanced version)
from crewai import Task

research_task = Task(
    description="""
    Conduct comprehensive research on the following topic: {topic}
    
    Your research must cover these dimensions:
    1. **Current State**: What's happening right now (last 3-6 months)
    2. **Historical Context**: How did we get here? Key milestones
    3. **Key Players**: Organizations, individuals, and their positions
    4. **Data & Statistics**: Concrete numbers, growth rates, market sizes
    5. **Controversies**: Debates, disagreements, unresolved questions
    6. **Future Trajectory**: Where experts think this is heading
    
    For each finding, note:
    - Source URL or citation
    - Your confidence level (High/Medium/Low)
    - Whether this is a primary or secondary source
    
    Format your output as a structured research brief with clear sections.
    Minimum 10 verified sources required.
    """,
    expected_output="A comprehensive research brief with minimum 10 sources, organized by theme, with confidence ratings",
    agent=researcher,
    async_execution=False
)

analysis_task = Task(
    description="""
    Analyze the research brief on: {topic}
    
    Your analysis should deliver:
    1. **Top 5 Insights**: The most significant findings, ranked by importance
    2. **Pattern Recognition**: Connections between seemingly unrelated findings
    3. **Confidence Assessment**: Which claims are solid vs which need more evidence
    4. **Gap Analysis**: What's missing from the research that would be valuable
    5. **Strategic Implications**: What these findings mean for decision-makers
    6. **Recommendations**: 3-5 actionable recommendations based on the analysis
    
    If you identify critical gaps, delegate back to the Researcher for follow-up.
    Use the Calculate Statistics tool if you need to analyze numerical data.
    """,
    expected_output="A strategic analysis document with confidence ratings, gap analysis, and actionable recommendations",
    agent=analyst,
    async_execution=False,
    context=[research_task]
)

fact_check_task = Task(
    description="""
    Review the research brief and analysis for: {topic}
    
    For each major claim:
    1. Can you independently verify it with a second source?
    2. Is the source credible and recent?
    3. Are there any contradictions between sources?
    4. Are any statistics misrepresented or taken out of context?
    
    Flag any issues with: 🔴 HIGH (likely incorrect), 🟡 MEDIUM (suspicious), 🟢 LOW (minor concern)
    
    If you find issues, delegate back to the Researcher for correction.
    """,
    expected_output="A quality assurance report with verified claims and flagged issues",
    agent=fact_checker,
    async_execution=False,
    context=[research_task, analysis_task]
)

writing_task = Task(
    description="""
    Based on the research, analysis, and fact-checking, write a professional report on: {topic}
    
    Structure the report as follows:
    
    1. **Executive Summary** (200 words max)
       - The one thing the reader must know
    
    2. **Key Findings** (bullet points, 5-7 items)
       - Each finding with supporting evidence
    
    3. **Detailed Analysis** (3-4 sections)
       - Deep dive into the most important themes
       - Data and evidence for each point
       - Conflicting viewpoints acknowledged
    
    4. **Strategic Recommendations** (3-5 items)
       - Specific, actionable, prioritized
    
    5. **Methodology & Sources**
       - How the research was conducted
       - List of sources with confidence ratings
    
    Tone: Professional, authoritative, engaging. Write for a C-suite audience.
    Length: 2000-2500 words.
    Format: Clean markdown with headers, bullet points, and emphasis where appropriate.
    """,
    expected_output="A polished, publication-ready report in markdown format (2000-2500 words)",
    agent=writer,
    async_execution=False,
    context=[research_task, analysis_task, fact_check_task]
)
