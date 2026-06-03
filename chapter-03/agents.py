# research_crew/agents.py
from crewai import Agent
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Optional

@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for current information on a topic."""
    search = DuckDuckGoSearchRun()
    return search.run(query)

@tool("Read URL")
def read_url(url: str) -> str:
    """Fetch and extract text content from a URL."""
    import requests
    from bs4 import BeautifulSoup
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator='\n', strip=True)[:8000]

researcher = Agent(
    role="Senior Research Analyst",
    goal="Find comprehensive, accurate, and up-to-date information on the given topic",
    backstory="""You're a veteran research analyst with 15 years of experience in market intelligence.
    You know exactly where to look for reliable data and how to verify sources.
    You prefer primary sources over secondary ones and always check your facts.""",
    tools=[web_search, read_url],
    verbose=True,
    allow_delegation=False,  # Researchers focus on research
    max_iterations=10,
    max_rpm=30,  # Rate limit to avoid API throttling
    llm="claude-mythos-5"  # Using Anthropic's flagship model
)

analyst = Agent(
    role="Data Analyst & Strategist",
    goal="Analyze research findings and extract actionable insights",
    backstory="""You're a strategic analyst who can spot patterns others miss.
    You transform raw data into clear, actionable recommendations.
    You're skilled at identifying trends, risks, and opportunities.""",
    tools=[web_search],  # Analysts may need to verify or supplement data
    verbose=True,
    allow_delegation=True,  # Analysts can delegate verification tasks back to researcher
    max_iterations=8,
    llm="gpt-5.5-thinking"  # Using OpenAI's reasoning model for analysis
)

writer = Agent(
    role="Technical Writer & Editor",
    goal="Synthesize research and analysis into clear, engaging, professional reports",
    backstory="""You're an award-winning technical writer who makes complex topics accessible.
    You structure information for maximum impact and readability.
    You know how to write for different audiences, from executives to engineers.""",
    tools=[],  # Writers don't need external tools
    verbose=True,
    allow_delegation=False,
    max_iterations=5,
    llm="claude-opus-4.8"  # Using Claude Opus for its exceptional writing quality
)
