# langgraph_agent/enhanced_graph.py (continued)
from .memory import EpisodicMemory, LongTermMemory

# Initialize memory systems
episodic_memory = EpisodicMemory()
long_term_memory = LongTermMemory()

# Initialize LLMs
reasoning_llm = ChatOpenAI(
    model="gpt-5.5-thinking",
    temperature=0.2,
    max_tokens=4096
)

action_llm = ChatOpenAI(
    model="gpt-5.5",
    temperature=0.3,
    max_tokens=2048
)

def should_use_episodic_memory(state: AgentState) -> AgentState:
    """Check if past similar experiences can guide current action."""
    current_context = state["messages"][-1].content if state["messages"] else ""
    similar_episodes = episodic_memory.retrieve_similar_episodes(current_context)
    
    if similar_episodes and similar_episodes[0]['similarity'] > 0.8:
        # Inject relevant past experience into context
        experience = similar_episodes[0]
        memory_note = f"[Episodic Memory] Similar past situation: {experience['action']} -> {experience['outcome']} (success: {experience['success_score']:.0%})"
        state["messages"].append(SystemMessage(content=memory_note))
    
    return state

def execute_with_memory(state: AgentState) -> AgentState:
    """Execute the agent's action and store the outcome."""
    # ... (action execution logic)
    
    # Store the episode
    episodic_memory.store_episode(
        user_id=state["user_id"],
        session_id=state["session_id"],
        action="searched_web",
        outcome=f"Found {len(state['search_results'])} results",
        success_score=0.9 if state["search_results"] else 0.0,
        context=state["messages"][-1].content
    )
    
    return state

# Build the enhanced graph
workflow = StateGraph(AgentState)

workflow.add_node("check_memory", should_use_episodic_memory)
workflow.add_node("search_web", search_web)
workflow.add_node("query_database", query_database)
workflow.add_node("generate_summary", generate_summary)
workflow.add_node("decide", decide_next_action)

workflow.set_entry_point("check_memory")
workflow.add_edge("check_memory", "decide")

# ... rest of the graph connections
