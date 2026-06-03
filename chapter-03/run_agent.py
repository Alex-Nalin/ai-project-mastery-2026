# run_agent.py
from langgraph_agent.graph import agent, AgentState

# Initialize state
initial_state = AgentState(
    messages=[HumanMessage(content="What are the latest developments in quantum computing for drug discovery?")],
    next_action="decide",
    search_results=[],
    db_results=[],
    final_summary="",
    iteration_count=0
)

# Configuration with thread_id for memory persistence
config = {"configurable": {"thread_id": "research_session_001"}}

# Run the agent
for event in agent.stream(initial_state, config):
    if "decide" in event:
        print(f"Decision: {event['decide']['next_action']}")
    elif "generate_summary" in event:
        print("\n=== FINAL SUMMARY ===")
        print(event["generate_summary"]["final_summary"])

# In a new session, the agent remembers previous context
new_query = AgentState(
    messages=[HumanMessage(content="Based on what we found earlier, how does this compare to traditional methods?")],
    next_action="decide",
    search_results=[],
    db_results=[],
    final_summary="",
    iteration_count=0
)

# Same thread_id = memory persists
for event in agent.stream(new_query, config):
    if "generate_summary" in event:
        print("\n=== FOLLOW-UP SUMMARY ===")
        print(event["generate_summary"]["final_summary"])
