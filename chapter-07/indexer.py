# research_assistant/indexer.py
"""Indexing and query engine for the research assistant."""

import os
from typing import List, Optional

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Settings,
    Document,
)
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.openai import OpenAI
import chromadb


class ResearchIndexer:
    """Create and manage the research index."""

    def __init__(self, persist_dir: str = "./research_db") -> None:
        self.persist_dir = persist_dir

        # Configure settings
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        Settings.llm = OpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=persist_dir)

    def create_index(
        self,
        documents: List[Document],
        collection_name: str = "research_knowledge",
    ) -> VectorStoreIndex:
        """Create a vector store index from documents."""
        # Create Chroma collection
        collection = self.chroma_client.get_or_create_collection(name=collection_name)
        vector_store = ChromaVectorStore(chroma_collection=collection)

        # Create storage context
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Create index
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True,
        )

        print(f"✓ Index created with {len(documents)} documents")
        return index

    def create_query_engine(
        self,
        index: VectorStoreIndex,
        similarity_top_k: int = 5,
        response_mode: str = "compact",
    ) -> RetrieverQueryEngine:
        """Create a query engine with citation support."""
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=similarity_top_k,
        )

        query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_mode=response_mode,
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)],
        )

        return query_engine

    def query_with_citations(
        self,
        query_engine: RetrieverQueryEngine,
        query: str,
    ) -> dict:
        """Query the engine and return response with citations."""
        response = query_engine.query(query)

        # Extract source information
        citations = []
        for node in response.source_nodes:
            citation = {
                "text": node.text[:200] + "...",
                "score": node.score,
                "source": node.metadata.get("source", "Unknown"),
                "source_type": node.metadata.get("source_type", "unknown"),
            }
            citations.append(citation)

        return {
            "query": query,
            "response": str(response),
            "citations": citations,
            "num_sources": len(citations),
        }
