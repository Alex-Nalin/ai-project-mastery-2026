# pgvector_setup.py
"""pgvector integration with LlamaIndex."""

import os
from llama_index.vector_stores.postgres import PGVectorStore


class PGVectorManager:
    """PostgreSQL + pgvector setup."""

    def __init__(self) -> None:
        self.connection_string = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

    def get_vector_store(self, table_name: str = "documents") -> PGVectorStore:
        """Get pgvector-backed vector store."""
        return PGVectorStore.from_params(
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST"),
            password=os.getenv("DB_PASSWORD"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER"),
            table_name=table_name,
            embed_dim=3072,
            hnsw_kwargs={
                "hnsw_ef_construction": 256,
                "hnsw_m": 16,
            },
        )
