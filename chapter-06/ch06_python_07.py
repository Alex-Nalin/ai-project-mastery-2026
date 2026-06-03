from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import tempfile
import os

app = FastAPI(title="Private Document Q&A")

# Initialize components
ingestor = DocumentIngestor()
engine = DocumentQueryEngine()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[str] = []

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document for indexing."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are supported")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        chunks = ingestor.ingest_document(tmp_path, {"filename": file.filename})
        return {"message": f"Ingested {chunks} chunks", "filename": file.filename}
    finally:
        os.unlink(tmp_path)

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the document store."""
    answer = await engine.query(request.question)
    return QueryResponse(answer=answer)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "collection": ingestor.collection_name}
