# multi_agent_system.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Optional
from dataclasses import dataclass, field
import asyncio
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

@dataclass
class AgentState:
    query: str
    plan: List[Dict] = field(default_factory=list)
    research_results: List[Dict] = field(default_factory=list)
    verified_results: List[Dict] = field(default_factory=list)
    final_response: str = ""
    errors: List[str] = field(default_factory=list)
    iteration_count: int = 0
    max_iterations: int = 5

class MultiAgentSystem:
    def __init__(self, openai_key: str, anthropic_key: str):
        self.openai_client = AsyncOpenAI(api_key=openai_key)
        self.anthropic_client = AsyncAnthropic(api_key=anthropic_key)
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("planner", self.planner_agent)
        workflow.add_node("researcher", self.researcher_agent)
        workflow.add_node("verifier", self.verifier_agent)
        workflow.add_node("summarizer", self.summarizer_agent)
        
        # Define edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "verifier")
        workflow.add_conditional_edges(
            "verifier",
            self.should_continue,
            {
                "iterate": "planner",
                "summarize": "summarizer"
            }
        )
        workflow.add_edge("summarizer", END)
        
        return workflow.compile()
    
    async def planner_agent(self, state: AgentState):
        """Break the query into sub-tasks"""
        response = await self.anthropic_client.messages.create(
            model="claude-opus-4.8",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"""You are a planning agent. Break this query into sub-tasks:
                
Query: {state.query}

Previous iterations: {len(state.research_results)}
Errors encountered: {state.errors}

Create a plan with:
1. Sub-tasks (each should be independently verifiable)
2. Dependencies between tasks
3. Required tools for each task
4. Success criteria

Output as JSON array of objects with keys: task_id, description, dependencies, tools, criteria"""
            }]
        )
        
        state.plan = response.content[0].text
        return state
    
    async def researcher_agent(self, state: AgentState):
        """Execute each sub-task"""
        results = []
        for task in state.plan:
            # Execute with appropriate tool
            result = await self._execute_task(task)
            results.append(result)
        
        state.research_results = results
        state.iteration_count += 1
        return state
    
    async def verifier_agent(self, state: AgentState):
        """Verify each result"""
        verified = []
        for result in state.research_results:
            verification = await self._verify_result(result)
            verified.append(verification)
        
        state.verified_results = verified
        return state
    
    def should_continue(self, state: AgentState):
        """Check if we need another iteration"""
        if state.iteration_count >= state.max_iterations:
            return "summarize"
        
        # Check if all verifications passed
        failures = [r for r in state.verified_results if not r.get("passed")]
        if not failures:
            return "summarize"
        
        return "iterate"
    
    async def summarizer_agent(self, state: AgentState):
        """Synthesize final response"""
        response = await self.openai_client.chat.completions.create(
            model="gpt-5.5-thinking",
            messages=[{
                "role": "system",
                "content": "Synthesize the verified research results into a coherent response."
            }, {
                "role": "user",
                "content": f"Query: {state.query}\n\nVerified Results: {state.verified_results}"
            }]
        )
        
        state.final_response = response.choices[0].message.content
        return state
    
    async def run(self, query: str) -> str:
        state = AgentState(query=query)
        final_state = await self.graph.ainvoke(state)
        return final_state["final_response"]
