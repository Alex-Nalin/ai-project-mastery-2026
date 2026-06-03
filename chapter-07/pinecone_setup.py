# pinecone_setup.py
"""Pinecone vector store setup and indexing."""

import os
from typing import List, Optional
import pinecone
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore


class PineconeManager:
    """Manage Pinecone vector store operations."""

    def __init__(self, index_name: str = "rag-knowledge-base") -> None:
        self.index_name = index_name
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENVIRONMENT", "us-east-1"),
        )

        # Create index if it doesn't exist
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=3072,  # text-embedding-3-large
                metric="cosine",
                spec=pinecone.ServerlessSpec(
                    cloud="aws",
                    region="us-east-1",
                ),
            )

    def create_index_from_nodes(self, nodes: List) -> VectorStoreIndex:
        """Create a LlamaIndex from pre-processed nodes."""
        vector_store = PineconeVectorStore(
            pinecone_index=self.index_name,
            namespace="default",
        )
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex(
            nodes=nodes,
            storage_context=storage_context,
            embed_model=Settings.embed_model,
        )
        return index

    def query_index(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[dict] = None,
    ) -> List:
        """Query the Pinecone index."""
        vector_store = PineconeVectorStore(
            pinecone_index=self.index_name,
            namespace="default",
        )
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=Settings.embed_model,
        )
        retriever = index.as_retriever(similarity_top_k=top_k, filters=filters)
        return retriever.retrieve(query)
