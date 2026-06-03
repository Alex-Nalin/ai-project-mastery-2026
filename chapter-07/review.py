# support_chatbot/review.py
"""Human review system for chatbot learning."""

from typing import List, Dict
from pydantic import BaseModel


class KnowledgeItem(BaseModel):
    content: str
    source_question: str
    timestamp: str
    reviewed: bool = False
    approved: bool = False


class KnowledgeReviewer:
    """Human-in-the-loop review for learned knowledge."""

    def __init__(self, vector_store) -> None:
        self.vector_store = vector_store
        self.pending_review: List[KnowledgeItem] = []

    def get_pending_review(self) -> List[Dict]:
        """Get items awaiting human review."""
        # Query for unverified documents
        results = self.vector_store.similarity_search(
            query="verified: False",
            k=50,
            filter={"verified": False},
        )

        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
            for doc in results
        ]

    def approve_knowledge(self, doc_id: str) -> None:
        """Approve a knowledge item."""
        # Update metadata
        self.vector_store.update_document(
            document_id=doc_id,
            metadata={"verified": True, "approved": True},
        )

    def reject_knowledge(self, doc_id: str) -> None:
        """Reject and remove a knowledge item."""
        self.vector_store.delete([doc_id])
