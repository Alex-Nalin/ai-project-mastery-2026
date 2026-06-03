from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import RouterQueryEngine

# Create specialized query engines
simple_engine = index.as_query_engine(similarity_top_k=3)
detailed_engine = index.as_query_engine(similarity_top_k=10)
multi_hop_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="tree_summarize",
)

# Create router
router = RouterQueryEngine.from_defaults(
    query_engine_tools=[
        QueryEngineTool(
            query_engine=simple_engine,
            metadata=ToolMetadata(
                name="simple_qa",
                description="For simple factual questions",
            ),
        ),
        QueryEngineTool(
            query_engine=detailed_engine,
            metadata=ToolMetadata(
                name="detailed_research",
                description="For complex questions needing multiple sources",
            ),
        ),
        QueryEngineTool(
            query_engine=multi_hop_engine,
            metadata=ToolMetadata(
                name="multi_hop",
                description="For questions requiring synthesis across topics",
            ),
        ),
    ]
)
