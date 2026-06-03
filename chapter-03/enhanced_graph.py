# langgraph_agent/enhanced_graph.py
from typing import TypedDict, Annotated, List, Literal, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint import MemorySaver
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
import sqlite3
import json
import hashlib
from datetime import datetime
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class AgentState(TypedDict):
    """Enhanced state with multiple memory types."""
    messages: Annotated[List[BaseMessage], "Full conversation history"]
    short_term_context: Annotated[List[str], "Recent context window"]
    long_term_memory: Annotated[Dict[str, Any], "Persistent knowledge store"]
    episodic_memory: Annotated[List[Dict], "Past action-outcome records"]
    search_results: List[str]
    db_results: List[dict]
    final_summary: str
    iteration_count: int
    user_id: str
    session_id: str
    confidence_scores: List[float]
