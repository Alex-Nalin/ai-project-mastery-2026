# Docker deployment (recommended for production)
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  -e N8N_SECURE_COOKIE=false \
  -e WEBHOOK_URL=https://your-domain.com \
  -e N8N_ENCRYPTION_KEY=your-encryption-key \
  n8nio/n8n

# Or with Docker Compose
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/home/node/.n8n
    environment:
      - N8N_SECURE_COOKIE=false
      - WEBHOOK_URL=https://your-domain.com
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
    restart: unless-stopped
EOF

docker-compose up -d
