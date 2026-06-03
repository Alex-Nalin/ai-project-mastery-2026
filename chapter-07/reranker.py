# research_assistant/reranker.py
"""Reranking with Cohere and BGE models."""

from typing import List
from llama_index.core.postprocessor import (
    CohereRerank,
    SentenceTransformerRerank,
)
from llama_index.core.schema import NodeWithScore
from llama_index.core import QueryBundle


class Reranker:
    """Rerank retrieved nodes for better relevance."""

    @staticmethod
    def get_cohere_reranker(
        model: str = "rerank-v3.5",
        top_n: int = 3,
    ) -> CohereRerank:
        """Get Cohere reranker."""
        return CohereRerank(
            model=model,
            top_n=top_n,
            api_key=os.getenv("COHERE_API_KEY"),
        )

    @staticmethod
    def get_bge_reranker(
        model: str = "BAAI/bge-reranker-v2-m3",
        top_n: int = 3,
    ) -> SentenceTransformerRerank:
        """Get BGE reranker (free, local)."""
        return SentenceTransformerRerank(
            model=model,
            top_n=top_n,
        )

    def rerank(
        self,
        nodes: List[NodeWithScore],
        query: str,
        reranker_type: str = "cohere",
    ) -> List[NodeWithScore]:
        """Rerank nodes using the specified model."""
        if reranker_type == "cohere":
            reranker = self.get_cohere_reranker()
        else:
            reranker = self.get_bge_reranker()

        return reranker.postprocess_nodes(
            nodes,
            query_bundle=QueryBundle(query_str=query),
        )
