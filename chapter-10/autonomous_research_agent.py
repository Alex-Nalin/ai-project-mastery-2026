# autonomous_research_agent.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Optional
from dataclasses import dataclass, field
import asyncio
from datetime import datetime
import json
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import numpy as np

@dataclass
class ResearchState:
    topic: str
    research_questions: List[str] = field(default_factory=list)
    hypotheses: List[Dict] = field(default_factory=list)
    evidence: List[Dict] = field(default_factory=list)
    contradictions: List[Dict] = field(default_factory=list)
    conclusions: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    iteration: int = 0
    max_iterations: int = 10
    quality_threshold: float = 0.85
    errors: List[str] = field(default_factory=list)
    execution_trace: List[Dict] = field(default_factory=list)

class AutonomousResearchAgent:
    def __init__(self, openai_key: str, anthropic_key: str):
        self.openai = AsyncOpenAI(api_key=openai_key)
        self.anthropic = AsyncAnthropic(api_key=anthropic_key)
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(ResearchState)
        
        # Research phases
        workflow.add_node("formulate_questions", self.formulate_questions)
        workflow.add_node("generate_hypotheses", self.generate_hypotheses)
        workflow.add_node("gather_evidence", self.gather_evidence)
        workflow.add_node("analyze_contradictions", self.analyze_contradictions)
        workflow.add_node("draw_conclusions", self.draw_conclusions)
        workflow.add_node("assess_quality", self.assess_quality)
        
        # Flow
        workflow.set_entry_point("formulate_questions")
        workflow.add_edge("formulate_questions", "generate_hypotheses")
        workflow.add_edge("generate_hypotheses", "gather_evidence")
        workflow.add_edge("gather_evidence", "analyze_contradictions")
        workflow.add_edge("analyze_contradictions", "draw_conclusions")
        workflow.add_edge("draw_conclusions", "assess_quality")
        
        # Quality gate
        workflow.add_conditional_edges(
            "assess_quality",
            self.decide_next_step,
            {
                "iterate": "formulate_questions",
                "complete": END
            }
        )
        
        return workflow.compile()
    
    async def formulate_questions(self, state: ResearchState):
        """Generate research questions from the topic"""
        response = await self.anthropic.messages.create(
            model="claude-opus-4.8",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"""You are a research methodology expert. Given this topic, generate the most important research questions that need to be answered for a comprehensive understanding.

Topic: {state.topic}

Previous iterations: {state.iteration}
Previous conclusions: {state.conclusions}
Identified gaps: {[e for e in state.errors if 'gap' in e.lower()]}

Generate 5-7 research questions that:
1. Cover different aspects of the topic
2. Are specific and answerable
3. Build on any previous findings
4. Address identified gaps

Output as a JSON array of strings."""
            }]
        )
        
        state.research_questions = json.loads(response.content[0].text)
        state.execution_trace.append({
            "phase": "formulate_questions",
            "timestamp": datetime.now().isoformat(),
            "output": state.research_questions
        })
        return state
    
    async def generate_hypotheses(self, state: ResearchState):
        """Generate testable hypotheses for each question"""
        hypotheses = []
        
        for question in state.research_questions:
            response = await self.openai.chat.completions.create(
                model="gpt-5.5-thinking",
                messages=[{
                    "role": "system",
                    "content": "Generate testable hypotheses. Each hypothesis must be falsifiable and have clear evidence criteria."
                }, {
                    "role": "user",
                    "content": f"Research Question: {question}\n\nGenerate 2-3 specific, testable hypotheses."
                }]
            )
            
            hypotheses.append({
                "question": question,
                "hypotheses": json.loads(response.choices[0].message.content)
            })
        
        state.hypotheses = hypotheses
        state.execution_trace.append({
            "phase": "generate_hypotheses",
            "timestamp": datetime.now().isoformat(),
            "output": len(hypotheses)
        })
        return state
    
    async def gather_evidence(self, state: ResearchState):
        """Gather evidence for each hypothesis"""
        evidence = []
        
        for hypothesis_group in state.hypotheses:
            for hypothesis in hypothesis_group["hypotheses"]:
                # Search for supporting evidence
                search_result = await self._search_evidence(hypothesis)
                
                # Analyze each piece of evidence
                for source in search_result:
                    analysis = await self._analyze_evidence(source, hypothesis)
                    evidence.append({
                        "hypothesis": hypothesis,
                        "source": source,
                        "analysis": analysis,
                        "relevance_score": analysis.get("relevance", 0.0)
                    })
        
        # Sort by relevance
        evidence.sort(key=lambda x: x["relevance_score"], reverse=True)
        state.evidence = evidence[:20]  # Keep top 20 pieces
        
        state.execution_trace.append({
            "phase": "gather_evidence",
            "timestamp": datetime.now().isoformat(),
            "output": len(evidence)
        })
        return state
    
    async def analyze_contradictions(self, state: ResearchState):
        """Identify contradictions in evidence"""
        contradictions = []
        
        # Compare evidence for conflicts
        for i, ev1 in enumerate(state.evidence):
            for ev2 in state.evidence[i+1:]:
                if self._evidence_conflicts(ev1, ev2):
                    contradiction = await self._resolve_contradiction(ev1, ev2)
                    contradictions.append(contradiction)
        
        state.contradictions = contradictions
        state.execution_trace.append({
            "phase": "analyze_contradictions",
            "timestamp": datetime.now().isoformat(),
            "output": len(contradictions)
        })
        return state
    
    async def draw_conclusions(self, state: ResearchState):
        """Draw conclusions from evidence"""
        response = await self.anthropic.messages.create(
            model="claude-opus-4.8",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"""Draw evidence-based conclusions from the following research:

Research Questions: {state.research_questions}
Hypotheses: {state.hypotheses}
Evidence: {state.evidence}
Contradictions: {state.contradictions}

For each conclusion:
1. State the conclusion clearly
2. List supporting evidence with citations
3. Note any caveats or limitations
4. Assess confidence level (0-1)

Output as JSON array of objects with keys: conclusion, evidence, caveats, confidence"""
            }]
        )
        
        state.conclusions = json.loads(response.content[0].text)
        state.execution_trace.append({
            "phase": "draw_conclusions",
            "timestamp": datetime.now().isoformat(),
            "output": len(state.conclusions)
        })
        return state
    
    async def assess_quality(self, state: ResearchState):
        """Assess the quality of the research"""
        response = await self.openai.chat.completions.create(
            model="gpt-5.5",
            messages=[{
                "role": "system",
                "content": """Assess research quality on these dimensions:
1. Coverage: Are all aspects of the topic addressed?
2. Evidence quality: Is the evidence strong and relevant?
3. Reasoning quality: Are conclusions logically supported?
4. Contradiction handling: Are contradictions properly addressed?
5. Novelty: Does the research provide new insights?

Score each dimension 0-1 and provide an overall score."""
            }, {
                "role": "user",
                "content": f"Research State: {json.dumps({
                    'questions': state.research_questions,
                    'hypotheses': state.hypotheses,
                    'evidence_count': len(state.evidence),
                    'contradictions': state.contradictions,
                    'conclusions': state.conclusions
                })}"
            }]
        )
        
        quality_assessment = json.loads(response.choices[0].message.content)
        state.quality_score = quality_assessment.get("overall_score", 0.0)
        
        # If quality is low, identify gaps for next iteration
        if state.quality_score < state.quality_threshold:
            state.errors.append(quality_assessment.get("gaps", "Quality below threshold"))
        
        state.execution_trace.append({
            "phase": "assess_quality",
            "timestamp": datetime.now().isoformat(),
            "output": state.quality_score
        })
        return state
    
    def decide_next_step(self, state: ResearchState):
        """Decide whether to iterate or complete"""
        if state.iteration >= state.max_iterations:
            return "complete"
        
        if state.quality_score >= state.quality_threshold:
            return "complete"
        
        state.iteration += 1
        return "iterate"
    
    async def _search_evidence(self, hypothesis: str) -> List[Dict]:
        """Search for evidence supporting or refuting a hypothesis"""
        # This would integrate with search APIs, databases, etc.
        # For demonstration, return simulated results
        return [
            {"source": f"research_paper_{i}", "content": f"Evidence related to: {hypothesis}", "relevance": np.random.random()}
            for i in range(3)
        ]
    
    async def _analyze_evidence(self, source: Dict, hypothesis: str) -> Dict:
        """Analyze a piece of evidence against a hypothesis"""
        response = await self.anthropic.messages.create(
            model="claude-opus-4.8",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""Analyze this evidence against the hypothesis:

Evidence: {source['content']}
Hypothesis: {hypothesis}

Assess:
1. Does it support or refute the hypothesis?
2. How strong is the evidence? (0-1)
3. Are there any methodological concerns?
4. What is the relevance to the original research question?

Output as JSON."""
            }]
        )
        
        return json.loads(response.content[0].text)
    
    def _evidence_conflicts(self, ev1: Dict, ev2: Dict) -> bool:
        """Check if two pieces of evidence conflict"""
        # Simple heuristic: check if they support different conclusions
        return ev1.get("analysis", {}).get("support") != ev2.get("analysis", {}).get("support")
    
    async def _resolve_contradiction(self, ev1: Dict, ev2: Dict) -> Dict:
        """Attempt to resolve a contradiction between evidence"""
        response = await self.anthropic.messages.create(
            model="claude-opus-4.8",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": f"""Resolve this contradiction:

Evidence 1: {ev1}
Evidence 2: {ev2}

Possible resolutions:
1. One piece of evidence is stronger
2. They address different aspects
3. There's a methodological difference
4. Both can be true under different conditions

Output resolution as JSON with: resolution_type, explanation, confidence"""
            }]
        )
        
        return json.loads(response.content[0].text)
    
    async def run(self, topic: str) -> ResearchState:
        """Execute the full research pipeline"""
        initial_state = ResearchState(topic=topic)
        final_state = await self.graph.ainvoke(initial_state)
        return final_state

# Usage
agent = AutonomousResearchAgent(
    openai_key="sk-...",
    anthropic_key="sk-ant-..."
)

result = await agent.run("The impact of 1-bit LLMs on edge AI deployment")

print(f"Quality Score: {result.quality_score}")
print(f"Iterations: {result.iteration}")
print(f"Conclusions: {len(result.conclusions)}")
for conclusion in result.conclusions:
    print(f"  - {conclusion['conclusion']} (Confidence: {conclusion['confidence']})")
