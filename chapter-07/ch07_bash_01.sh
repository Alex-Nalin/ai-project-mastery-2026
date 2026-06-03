# Create project directory
mkdir research-assistant
cd research-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install llama-index==0.12.4 \
    llama-index-readers-file==0.2.0 \
    llama-index-readers-web==0.3.1 \
    llama-index-readers-youtube-transcript==0.1.0 \
    llama-index-embeddings-openai==0.3.0 \
    llama-index-vector-stores-chroma==0.2.0 \
    openai==1.60.0 \
    chromadb==0.5.0 \
    pypdf==5.0.0 \
    beautifulsoup4==4.13.0 \
    youtube-transcript-api==0.6.0 \
    fastapi==0.115.0 \
    uvicorn==0.30.0
