# Install dependencies
pip install qdrant-client nomic sentence-transformers pypdf2 ollama

# Start Qdrant (Docker)
docker run -d -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Verify Ollama is running
curl http://localhost:11434/api/tags
