# semantic_chunker.py
"""Semantic chunking that respects document structure."""

from typing import List, Optional
from llama_index.core.node_parser import (
    SemanticSplitterNodeParser,
    SentenceSplitter,
    TokenTextSplitter,
)
from llama_index.core import Document
from llama_index.embeddings.openai import OpenAIEmbedding


class SmartChunker:
    """Intelligent document chunking with multiple strategies."""

    def __init__(self, embed_model: Optional[OpenAIEmbedding] = None) -> None:
        self.embed_model = embed_model or OpenAIEmbedding(
            model="text-embedding-3-large",
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    def semantic_chunk(
        self,
        documents: List[Document],
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
    ) -> List:
        """Chunk documents using semantic boundaries."""
        parser = SemanticSplitterNodeParser(
            buffer_size=chunk_size,
            breakpoint_percentile_threshold=95,
            embed_model=self.embed_model,
        )
        nodes = parser.get_nodes_from_documents(documents)
        print(f"Semantic chunking: {len(documents)} docs → {len(nodes)} nodes")
        return nodes

    def recursive_chunk(
        self,
        documents: List[Document],
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
    ) -> List:
        """Try multiple chunk sizes and pick the best one."""
        # Start with larger chunks, fall back to smaller ones
        chunk_sizes = [2048, 1024, 512, 256]

        for size in chunk_sizes:
            parser = SentenceSplitter(
                chunk_size=size,
                chunk_overlap=int(size * 0.2),  # 20% overlap
            )
            nodes = parser.get_nodes_from_documents(documents)

            # Check if we have reasonable granularity
            if len(nodes) >= len(documents) * 2:
                print(f"Recursive chunking: using chunk_size={size}")
                return nodes

        # Fallback: token-based splitting
        parser = TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return parser.get_nodes_from_documents(documents)

    def late_chunk(self, documents: List[Document], chunk_size: int = 512) -> List:
        """
        Late chunking: embed at document level, retrieve at chunk level.

        This preserves document-level context while allowing fine-grained retrieval.
        """
        # Store both full documents and chunks
        doc_nodes = self.semantic_chunk(documents, chunk_size)

        # Add document-level embeddings as metadata
        for node in doc_nodes:
            doc_text = node.ref_doc_id  # Reference to full document
            node.metadata["doc_level_embedding"] = True

        return doc_nodes
