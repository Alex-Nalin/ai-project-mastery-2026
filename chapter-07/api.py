# research_assistant/api.py
"""FastAPI web application for the research assistant."""

import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .ingestion import ResearchIngestion
from .indexer import ResearchIndexer

app = FastAPI(
    title="Research Assistant API",
    description="Multi-source research assistant with citations",
    version="1.0.0",
)

# Initialize components
ingestion = ResearchIngestion()
indexer = ResearchIndexer()

# Global index (loaded on startup)
research_index = None
query_engine = None


class IngestRequest(BaseModel):
    pdfs: Optional[List[str]] = None
    urls: Optional[List[str]] = None
    videos: Optional[List[str]] = None


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


@app.on_event("startup")
async def startup_event() -> None:
    """Load or create index on startup."""
    global research_index, query_engine

    # Check if index exists
    try:
        collection = indexer.chroma_client.get_collection("research_knowledge")
        if collection.count() > 0:
            # Load existing index
            from llama_index.core import VectorStoreIndex
            from llama_index.vector_stores.chroma import ChromaVectorStore

            vector_store = ChromaVectorStore(chroma_collection=collection)
            research_index = VectorStoreIndex.from_vector_store(vector_store)
            query_engine = indexer.create_query_engine(research_index)
            print("✓ Loaded existing index")
    except Exception:
        print("No existing index found. Ingest documents first.")


@app.post("/ingest")
async def ingest_documents(request: IngestRequest) -> dict:
    """Ingest documents from multiple sources."""
    global research_index, query_engine

    try:
        # Ingest documents
        documents = ingestion.ingest_all(
            pdfs=request.pdfs,
            urls=request.urls,
            videos=request.videos,
        )

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No documents were successfully ingested",
            )

        # Create index
        research_index = indexer.create_index(documents)
        query_engine = indexer.create_query_engine(research_index)

        return {
            "status": "success",
            "documents_ingested": len(documents),
            "sources": {
                "pdfs": len(request.pdfs or []),
                "urls": len(request.urls or []),
                "videos": len(request.videos or []),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}",
        )


@app.post("/query")
async def query_knowledge_base(request: QueryRequest) -> dict:
    """Query the knowledge base with citations."""
    global query_engine

    if not query_engine:
        raise HTTPException(
            status_code=400,
            detail="No documents ingested yet. POST to /ingest first.",
        )

    try:
        result = indexer.query_with_citations(query_engine, request.query)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}",
        )


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "index_loaded": research_index is not None,
    }
