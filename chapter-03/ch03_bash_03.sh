cat > .env << 'EOF'
# Required: At least one LLM provider
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Optional: For enhanced search capabilities
SERPER_API_KEY=your-serper-api-key  # If using Google Search via Serper
TAVILY_API_KEY=your-tavily-api-key   # If using Tavily for AI-optimized search

# Optional: For saving reports to cloud storage
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-reports-bucket
EOF
