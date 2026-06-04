# Start the server
python bitnet_server.py

# In another terminal, test it
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain the benefits of 1-bit LLMs in three sentences.", "max_tokens": 100}'
