# research_assistant/hybrid_retrieval.py
"""Hybrid retrieval combining vector search and BM25."""

from typing import List, Optional
from llama_index.core.retrievers import (
    VectorIndexRetriever,
    KeywordTableRetriever,
)
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore


class HybridRetriever:
    """Combine vector and keyword retrieval for better results."""

    def __init__(
        self,
        vector_retriever: VectorIndexRetriever,
        keyword_retriever: KeywordTableRetriever,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ) -> None:
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight

    def retrieve(self, query: str, top_k: int = 5) -> List[NodeWithScore]:
        """Retrieve using hybrid approach."""
        # Get results from both retrievers
        query_bundle = QueryBundle(query_str=query)

        vector_results = self.vector_retriever.retrieve(query_bundle)
        keyword_results = self.keyword_retriever.retrieve(query_bundle)

        # Merge and re-rank
        merged: dict = {}

        for node in vector_results:
            merged[node.node.node_id] = {
                "node": node,
                "score": node.score * self.vector_weight,
            }

        for node in keyword_results:
            if node.node.node_id in merged:
                merged[node.node.node_id]["score"] += node.score * self.keyword_weight
            else:
                merged[node.node.node_id] = {
                    "node": node,
                    "score": node.score * self.keyword_weight,
                }

        # Sort by combined score and return top_k
        sorted_results = sorted(
            merged.values(),
            key=lambda x: x["score"],
            reverse=True,
        )

        return [r["node"] for r in sorted_results[:top_k]]
