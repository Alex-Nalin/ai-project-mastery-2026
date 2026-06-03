import os
from typing import List, Dict
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uuid

class DocumentIngestor:
    """Ingests documents into Qdrant vector store."""
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "documents",
        embedding_model: str = "nomic-embed-text-v1.5"
    ):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name


```python
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Create collection if it doesn't exist
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create the Qdrant collection with proper configuration."""
        collections = self.qdrant.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_model.get_sentence_embedding_dimension(),
                    distance=models.Distance.COSINE
                )
            )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap
        return chunks
    
    def ingest_document(self, pdf_path: str, metadata: Dict = None):
        """Ingest a single PDF document."""
        # Extract and chunk
        text = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_text(text)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(chunks)
        
        # Prepare points for Qdrant
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            points.append(models.PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload={
                    "text": chunk,
                    "source": os.path.basename(pdf_path),
                    "chunk_index": i,
                    "metadata": metadata or {}
                }
            ))
        
        # Upload to Qdrant
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return len(chunks)
    
    def ingest_directory(self, directory_path: str, metadata: Dict = None):
        """Ingest all PDFs in a directory."""
        total_chunks = 0
        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(directory_path, filename)
                chunks = self.ingest_document(pdf_path, metadata)
                total_chunks += chunks
                print(f"Ingested {filename}: {chunks} chunks")
        return total_chunks

class DocumentQueryEngine:
    """Queries documents using RAG pipeline."""
    
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "documents",
        ollama_url: str = "http://localhost:11434",
        model: str = "qwen3.5:32b",
        top_k: int = 3
    ):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.ollama_url = ollama_url
        self.model = model
        self.top_k = top_k
        self.embedding_model = SentenceTransformer("nomic-embed-text-v1.5")
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def retrieve_relevant_chunks(self, query: str) -> List[str]:
        """Retrieve relevant document chunks for a query."""
        # Embed the query
        query_embedding = self.embedding_model.encode(query)
        
        # Search Qdrant
        search_result = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=self.top_k
        )
        
        return [hit.payload["text"] for hit in search_result]
    
    async def query(self, question: str) -> str:
        """Answer a question using RAG."""
        # Retrieve relevant context
        chunks = await self.retrieve_relevant_chunks(question)
        
        # Build prompt with context
        context = "\n\n".join(chunks)
        prompt = f"""Based on the following documents, answer the question.

Context:
{context}

Question: {question}

Answer the question using only the information provided in the context. If the answer cannot be found in the context, say "I cannot find this information in the provided documents."
"""
        
        # Query Ollama
        response = await self.client.post(
            f"{self.ollama_url}/api/chat",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": 0.3, "num_predict": 1024}
            }
        )
        
        result = response.json()
        return result["message"]["content"]
    
    async def close(self):
        await self.client.aclose()

# Usage
async def main():
    # Ingest documents
    ingestor = DocumentIngestor()
    ingestor.ingest_directory("./contracts")
    
    # Query
    engine = DocumentQueryEngine()
    answer = await engine.query("What is the termination clause in the service agreement?")
    print(answer)
    await engine.close()
