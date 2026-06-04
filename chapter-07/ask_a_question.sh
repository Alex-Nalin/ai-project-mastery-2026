# Ask a question
curl -X POST http://

```bash
# Ask a question
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key challenges in quantum error correction?",
    "top_k": 5
  }'
