# qdrant_setup.py
"""Qdrant vector store setup - self-hosted or cloud."""

import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from llama_index.vector_stores.qdrant import QdrantVectorStore


class QdrantManager:
    """Manage Qdrant vector store."""

    def __init__(self, use_local: bool = True) -> None:
        if use_local:
            # Local Qdrant instance
            self.client = QdrantClient(host="localhost", port=6333)
        else:
            # Qdrant Cloud
            self.client = QdrantClient(
                url=os.getenv("QDRANT_URL"),
                api_key=os.getenv("QDRANT_API_KEY"),
            )

    def create_collection(self, collection_name: str, dimension: int = 3072) -> None:
        """Create a new collection."""
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )

    def get_vector_store(self, collection_name: str) -> QdrantVectorStore:
        """Get LlamaIndex-compatible vector store."""
        return QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
        )
