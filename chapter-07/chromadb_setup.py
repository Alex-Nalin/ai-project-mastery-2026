# chromadb_setup.py
"""Quick-start with ChromaDB for prototyping."""

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore


class ChromaManager:
    """Lightweight ChromaDB setup for prototyping."""

    def __init__(self, persist_dir: str = "./chroma_db") -> None:
        self.client = chromadb.PersistentClient(path=persist_dir)

    def get_or_create_collection(self, name: str):
        """Get or create a collection."""
        return self.client.get_or_create_collection(name)

    def get_vector_store(self, collection_name: str) -> ChromaVectorStore:
        """Get LlamaIndex-compatible vector store."""
        collection = self.get_or_create_collection(collection_name)
        return ChromaVectorStore(chroma_collection=collection)
