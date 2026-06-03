# embedding_selector.py
"""Embedding model selection and management."""

import os
from typing import Optional
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.cohere import CohereEmbedding


class EmbeddingManager:
    """Manage embedding models for different use cases."""

    @staticmethod
    def get_openai_embedding(
        model: str = "text-embedding-3-large",
        dimensions: int = 3072,
    ) -> OpenAIEmbedding:
        """Get OpenAI embedding model."""
        return OpenAIEmbedding(
            model=model,
            dimensions=dimensions,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    @staticmethod
    def get_cohere_embedding(
        model: str = "embed-v4",
        input_type: str = "search_document",
    ) -> CohereEmbedding:
        """Get Cohere embedding model."""
        return CohereEmbedding(
            model=model,
            input_type=input_type,
            api_key=os.getenv("COHERE_API_KEY"),
        )

    @staticmethod
    def configure_settings(
        embed_model: str = "openai",
        llm_model: str = "gpt-4o",
    ) -> None:
        """Configure global LlamaIndex settings."""
        if embed_model == "openai":
            Settings.embed_model = OpenAIEmbedding(
                model="text-embedding-3-large",
                dimensions=3072,
            )
        elif embed_model == "cohere":
            Settings.embed_model = CohereEmbedding(
                model="embed-v4",
                input_type="search_document",
            )

        Settings.llm = f"openai/{llm_model}"
        Settings.chunk_size = 1024
        Settings.chunk_overlap = 200
