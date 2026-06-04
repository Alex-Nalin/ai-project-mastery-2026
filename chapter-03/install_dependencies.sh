mkdir research-crew && cd research-crew
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install crewai==0.108.0 crewai-tools==0.18.0 langchain-community==0.3.0 \
            langchain-openai==0.2.0 python-dotenv==1.0.0 beautifulsoup4==4.12.0 \
            requests==2.31.0 duckduckgo-search==6.2.0
