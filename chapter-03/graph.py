# langgraph_agent/graph.py
from typing import TypedDict, Annotated, List, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
import sqlite3
import json

# Define the state schema
class AgentState(TypedDict):
    messages: Annotated[List, "Conversation history"]
    next_action: str
    search_results: List[str]
    db_results: List[dict]
    final_summary: str
    iteration_count: int
    
# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-5.5",
    temperature=0.3,
    max_tokens=4096
)

# Tool functions
def search_web(state: AgentState) -> AgentState:
    """Search the web for current information."""
    search = DuckDuckGoSearchRun()
    last_message = state["messages"][-1].content
    
    # Extract search query from the last message
    query = f"Latest information about: {last_message[:200]}"
    results = search.run(query)
    
    state["search_results"].append(results)
    state["messages"].append(AIMessage(content=f"Search results: {results[:2000]}"))
    state["iteration_count"] += 1
    return state

def query_database(state: AgentState) -> AgentState:
    """Query a SQLite database for relevant records."""
    conn = sqlite3.connect("knowledge_base.db")
    cursor = conn.cursor()
    
    # Simple keyword matching for demonstration
    last_message = state["messages"][-1].content.lower()
    
    # Extract potential keywords
    keywords = [word for word in last_message.split() if len(word) > 3][:5]
    
    results = []
    for keyword in keywords:
        cursor.execute(
            "SELECT title, content, source FROM documents WHERE content LIKE ? LIMIT 3",
            (f"%{keyword}%",)
        )
        rows = cursor.fetchall()
        for row in rows:
            results.append({"title": row[0], "content": row[1][:500], "source": row[2]})
    
    conn.close()
    
    state["db_results"].extend(results)
    state["messages"].append(AIMessage(content=f"Database results: {json.dumps(results, indent=2)}"))
    state["iteration_count"] += 1
    return state

def decide_next_action(state: AgentState) -> Literal["search_web", "query_database", "generate_summary", "end"]:
    """Use the LLM to decide what to do next."""
    system_prompt = """You are an autonomous research agent. Based on the conversation so far, decide what to do next:

- If you need more current information, choose 'search_web'
- If you need to check your knowledge base, choose 'query_database'
- If you have enough information to produce a summary, choose 'generate_summary'
- If the task is complete or you've reached the maximum iterations, choose 'end'

Respond with exactly one word: search_web, query_database, generate_summary, or end."""

    messages = [
        SystemMessage(content=system_prompt),
        *state["messages"][-5:]  # Last 5 messages for context
    ]
    
    response = llm.invoke(messages)
    decision = response.content.strip().lower()
    
    # Validate the decision
    valid_actions = ["search_web", "query_database", "generate_summary", "end"]
    if decision not in valid_actions:
        decision = "generate_summary"
    
    # Safety: limit iterations to prevent infinite loops
    if state["iteration_count"] >= 5:
        decision = "generate_summary"
    
    state["next_action"] = decision
    return decision

def generate_summary(state: AgentState) -> AgentState:
    """Generate the final summary using all gathered information."""
    system_prompt = """You are a research synthesis expert. 
    Create a comprehensive, well-structured summary based on all the information gathered.
    Include citations where possible. Organize the summary with clear sections."""

    messages = [
        SystemMessage(content=system_prompt),
        *state["messages"]
    ]
    
    response = llm.invoke(messages)
    state["final_summary"] = response.content
    state["next_action"] = "end"
    return state

def should_continue(state: AgentState) -> Literal["continue", "end"]:
    """Check if we should continue or end the process."""
    if state["next_action"] == "end":
        return "end"
    if state["iteration_count"] >= 5:
        return "end"
    return "continue"

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("search_web", search_web)
workflow.add_node("query_database", query_database)
workflow.add_node("generate_summary", generate_summary)
workflow.add_node("decide", decide_next_action)

# Set entry point
workflow.set_entry_point("decide")

# Add conditional edges
workflow.add_conditional_edges(
    "decide",
    lambda state: state["next_action"],
    {
        "search_web": "search_web",
        "query_database": "query_database",
        "generate_summary": "generate_summary",
        "end": END
    }
)

# Add edges from action nodes back to decision
workflow.add_edge("search_web", "decide")
workflow.add_edge("query_database", "decide")
workflow.add_edge("generate_summary", END)

# Add memory checkpointing
memory = MemorySaver()

# Compile the graph
agent = workflow.compile(checkpointer=memory)
