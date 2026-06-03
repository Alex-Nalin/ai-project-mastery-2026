# agents.py (enhanced version)
from crewai import Agent
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Optional
import json

@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for current information. Use this for finding recent news, 
    articles, and general information on any topic."""
    search = DuckDuckGoSearchRun()
    try:
        results = search.run(query)
        return results[:5000]  # Limit to avoid context overflow
    except Exception as e:
        return f"Search failed: {str(e)}"

@tool("Read URL")
def read_url(url: str) -> str:
    """Fetch and extract the main text content from a URL. 
    Use this to read specific articles, documentation, or web pages."""
    import requests
    from bs4 import BeautifulSoup
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove non-content elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        
        # Get text, clean up whitespace
        text = soup.get_text(separator='\n', strip=True)
        lines = [line for line in text.split('\n') if line.strip()]
        clean_text = '\n'.join(lines)
        
        return clean_text[:8000]  # Limit length
    except Exception as e:
        return f"Failed to read URL: {str(e)}"

@tool("Calculate Statistics")
def calculate_statistics(data_json: str) -> str:
    """Perform basic statistical calculations on a JSON array of numbers.
    Input should be a JSON string like '[1, 2, 3, 4, 5]'.
    Returns mean, median, standard deviation, min, and max."""
    import statistics
    import json
    
    try:
        data = json.loads(data_json)
        if not isinstance(data, list) or not all(isinstance(x, (int, float)) for x in data):
            return "Error: Input must be a JSON array of numbers"
        
        return json.dumps({
            "mean": statistics.mean(data),
            "median": statistics.median(data),
            "stdev": statistics.stdev(data) if len(data) > 1 else 0,
            "min": min(data),
            "max": max(data),
            "count": len(data)
        }, indent=2)
    except Exception as e:
        return f"Calculation error: {str(e)}"

# Define agents with enhanced capabilities
researcher = Agent(
    role="Senior Research Analyst",
    goal="Find comprehensive, accurate, and up-to-date information on the given topic. "
         "You prioritize primary sources, verify facts across multiple sources, and "
         "provide context for all findings.",
    backstory="""You're a veteran research analyst with 15 years of experience in market 
    intelligence and academic research. You've worked at top consulting firms and know 
    exactly how to separate signal from noise. You're meticulous about source quality 
    and always note your confidence level for each finding.""",
    tools=[web_search, read_url],
    verbose=True,
    allow_delegation=False,
    max_iterations=15,
    max_rpm=30,
    llm="claude-mythos-5"
)

analyst = Agent(
    role="Data Analyst & Strategist",
    goal="Transform raw research into actionable strategic insights. Identify patterns, "
         "assess implications, and provide clear recommendations backed by evidence.",
    backstory="""You're a former McKinsey consultant turned independent strategist. 
    You've helped dozens of companies make critical decisions based on market analysis. 
    You're skilled at quantitative analysis, trend identification, and risk assessment. 
    You don't just present data—you tell leaders what it means and what to do about it.""",
    tools=[web_search, calculate_statistics],
    verbose=True,
    allow_delegation=True,
    max_iterations=10,
    llm="gpt-5.5-thinking"
)

writer = Agent(
    role="Executive Communications Director",
    goal="Synthesize complex research and analysis into clear, compelling, and "
         "actionable reports that executives can read in minutes and act on immediately.",
    backstory="""You've spent a decade as a communications director for Fortune 500 CEOs. 
    You know that executives don't have time to wade through details—they need the 
    bottom line up front, with supporting evidence organized for quick scanning. 
    You're a master of structure, tone, and persuasive writing.""",
    tools=[],
    verbose=True,
    allow_delegation=False,
    max_iterations=8,
    llm="claude-opus-4.8"
)

fact_checker = Agent(
    role="Fact Checker & Quality Assurance",
    goal="Verify all claims, statistics, and assertions in the research. Flag any "
         "unsubstantiated claims, contradictions, or potential hallucinations.",
    backstory="""You're a former fact-checker for a major news organization. You've 
    built your career on catching errors that everyone else missed. You're skeptical 
    by nature and demand evidence for every claim. Your motto: 'Trust, but verify.'""",
    tools=[web_search, read_url],
    verbose=True,
    allow_delegation=True,
    max_iterations=10,
    llm="gpt-5.5"  # Cost-effective for verification tasks
)
