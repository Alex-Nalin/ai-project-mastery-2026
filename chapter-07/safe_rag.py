# safe_rag.py
"""RAG system with hallucination prevention."""

from llama_index.core.postprocessor import SimilarityPostprocessor


class SafeRAG:
    """RAG system that knows when to say 'I don't know'."""

    def __init__(self, query_engine, confidence_threshold: float = 0.7) -> None:
        self.query_engine = query_engine
        self.confidence_threshold = confidence_threshold

    def query(self, query: str) -> dict:
        """Query with confidence check."""
        response = self.query_engine.query(query)

        # Check confidence of retrieved documents
        max_confidence = max(
            (n.score for n in response.source_nodes),
            default=0,
        )

        if max_confidence < self.confidence_threshold:
            return {
                "answer": "I don't have sufficient information "
                "to answer this question accurately.",
                "confidence": max_confidence,
                "sources": [],
            }

        return {
            "answer": str(response),
            "confidence": max_confidence,
            "sources": [
                {
                    "source": n.metadata.get("source", "Unknown"),
                    "relevance": n.score,
                }
                for n in response.source_nodes
            ],
        }
