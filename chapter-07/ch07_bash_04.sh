# Ingest some research materials
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "pdfs": ["./research_data/pdfs/paper1.pdf"],
    "urls": ["https://en.wikipedia.org/wiki/Quantum_computing"],
    "videos": ["dQw4w9WgXcQ"]
  }'
