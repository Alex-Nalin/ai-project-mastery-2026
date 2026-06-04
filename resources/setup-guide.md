# Appendix B: Complete Project Code and GitHub Repository Guide

## Introduction: The Blueprint for AI Project Success

In April 2026, the AI development landscape has matured into a sophisticated ecosystem where building production-grade AI applications requires more than just writing good prompts. According to the 2026 State of AI Development Report, 78% of AI projects fail to reach production due to poor project structure, inadequate environment management, and deployment complexities. The difference between a successful AI product and an abandoned prototype often comes down to how well you organize your code, manage dependencies, and set up your deployment pipeline.

This appendix serves as your comprehensive reference for everything you need to take the projects in this book from your local development environment to production deployment. We've compiled environment setup scripts for all major operating systems, complete dependency management files, Docker configurations for self-hosted AI tools, deployment guides for every platform we use, and a troubleshooting FAQ covering the most common errors you'll encounter. By the end of this appendix, you'll have a battle-tested template for structuring any AI project that scales from solo development to team collaboration.

## What You Will Build

1. **A Complete Multi-Platform Development Environment** – Cross-platform setup scripts that configure Python 3.12+, GPU acceleration, API keys, and all dependencies for Windows, macOS, and Linux
2. **Docker-Based AI Infrastructure** – Production-ready Docker Compose configurations for self-hosted tools including n8n, Qdrant, Open WebUI, and Ollama
3. **Deployment Pipeline Templates** – Step-by-step deployment guides for Vercel, Railway, Render, and Hugging Face Spaces with CI/CD integration

## Section 1: Environment Setup Scripts

### 1.1 Python Environment Configuration

The foundation of any AI project in 2026 is a properly configured Python environment. We use Python 3.12+ for its improved performance, better error messages, and enhanced async support. Below are complete setup scripts for each operating system.

#### Windows Setup Script

Create a file named `setup_windows.ps1` with the following content:

```powershell
# Windows AI Project Environment Setup Script
# Requires: Windows 10/11, PowerShell 5.1+, Administrator privileges for GPU setup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Project Environment Setup (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check Python installation
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.(1[2-9]|[2-9]\d)") {
    Write-Host "✓ Python $pythonVersion detected" -ForegroundColor Green
} else {
    Write-Host "✗ Python 3.12+ required. Installing..." -ForegroundColor Yellow
    $pythonInstaller = "python-3.12.3-amd64.exe"
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.3/$pythonInstaller" -OutFile "$env:TEMP\$pythonInstaller"
    Start-Process -Wait -FilePath "$env:TEMP\$pythonInstaller" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1"
    Write-Host "✓ Python 3.12.3 installed" -ForegroundColor Green
}

# Install Miniconda if not present
if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Miniconda..." -ForegroundColor Yellow
    $condaInstaller = "Miniconda3-latest-Windows-x86_64.exe"
    Invoke-WebRequest -Uri "https://repo.anaconda.com/miniconda/$condaInstaller" -OutFile "$env:TEMP\$condaInstaller"
    Start-Process -Wait -FilePath "$env:TEMP\$condaInstaller" -ArgumentList "/InstallationType=JustMe /RegisterPython=0 /S /D=%USERPROFILE%\Miniconda3"
    Write-Host "✓ Miniconda installed" -ForegroundColor Green
}

# Create conda environment
Write-Host "Creating AI project environment..." -ForegroundColor Yellow
conda create -n ai_projects python=3.12 -y
conda activate ai_projects

# Install core packages
Write-Host "Installing core packages..." -ForegroundColor Yellow
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install langchain==0.3.15 langchain-community langchain-openai langchain-anthropic
pip install llama-index==0.12.8
pip install crewai==0.108.0
pip install fastapi uvicorn[standard]
pip install python-dotenv pydantic pydantic-settings
pip install qdrant-client chromadb
pip install openai anthropic google-generativeai
pip install transformers accelerate bitsandbytes
pip install jupyter notebook ipykernel
pip install black ruff mypy pytest pytest-asyncio

# Create project structure
Write-Host "Creating project directories..." -ForegroundColor Yellow
$directories = @(
    "src", "src/agents", "src/apps", "src/automations", "src/business",
    "tests", "tests/unit", "tests/integration",
    "config", "data", "data/raw", "data/processed",
    "notebooks", "scripts", "docker", "deployment",
    "docs", ".github/workflows"
)
foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# Create .env template
$envTemplate = @"
# API Keys - Replace with your actual keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-api-key
GROQ_API_KEY=your-groq-api-key

# Vector Database Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-key
CHROMA_PERSIST_DIR=./data/chromadb

# Model Configuration
OPENAI_MODEL=gpt-5.5
ANTHROPIC_MODEL=claude-opus-4.8
LOCAL_MODEL=qwen3.5:72b

# Application Settings
LOG_LEVEL=INFO
MAX_TOKENS=8192
TEMPERATURE=0.7
"@
Set-Content -Path ".env.example" -Value $envTemplate

# Create requirements.txt
$requirements = @"
# Core AI Frameworks
langchain==0.3.15
langchain-community==0.3.15
langchain-openai==0.3.2
langchain-anthropic==0.3.4
llama-index==0.12.8
crewai==0.108.0

# Web Framework
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
pydantic-settings==2.7.1

# Vector Databases
qdrant-client==1.13.0
chromadb==0.6.3

# AI Providers
openai==1.58.1
anthropic==0.49.0
google-generativeai==0.8.4

# Machine Learning
torch>=2.5.0
transformers==4.48.3
accelerate==1.3.0
bitsandbytes==0.45.2

# Development Tools
python-dotenv==1.0.1
jupyter==1.1.1
ipykernel==6.29.5
black==24.10.0
ruff==0.8.6
mypy==1.14.1
pytest==8.3.4
pytest-asyncio==0.25.0

# Utilities
httpx==0.28.1
aiohttp==3.11.11
tqdm==4.67.1
rich==13.9.4
"@
Set-Content -Path "requirements.txt" -Value $requirements

Write-Host "✓ Windows environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env.example to add your API keys and rename to .env"
Write-Host "2. Activate environment: conda activate ai_projects"
Write-Host "3. Start building: cd src && python your_project.py"
```

#### macOS Setup Script

Create `setup_macos.sh`:

```bash
#!/bin/bash
# macOS AI Project Environment Setup Script
# Requires: macOS 14+ (Sonoma), Homebrew, Xcode Command Line Tools

set -e

echo "========================================"
echo "  AI Project Environment Setup (macOS)"
echo "========================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}Installing Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Xcode Command Line Tools
if ! xcode-select -p &> /dev/null; then
    echo -e "${YELLOW}Installing Xcode Command Line Tools...${NC}"
    xcode-select --install
fi

# Install Python 3.12
if ! python3.12 --version &> /dev/null; then
    echo -e "${YELLOW}Installing Python 3.12...${NC}"
    brew install python@3.12
fi

# Install Miniconda
if ! command -v conda &> /dev/null; then
    echo -e "${YELLOW}Installing Miniconda...${NC}"
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p $HOME/miniconda
    eval "$($HOME/miniconda/bin/conda shell.bash hook)"
    conda init
fi

# Create conda environment
echo -e "${YELLOW}Creating AI project environment...${NC}"
conda create -n ai_projects python=3.12 -y
conda activate ai_projects

# Install core packages
echo -e "${YELLOW}Installing core packages...${NC}"
pip install --upgrade pip

# PyTorch with MPS support (Apple Silicon)
if [[ $(uname -m) == 'arm64' ]]; then
    pip install torch torchvision torchaudio
else
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# AI Frameworks
pip install langchain==0.3.15 langchain-community langchain-openai langchain-anthropic
pip install llama-index==0.12.8
pip install crewai==0.108.0

# Web and API
pip install fastapi uvicorn[standard]
pip install python-dotenv pydantic pydantic-settings

# Vector Databases
pip install qdrant-client chromadb

# AI Providers
pip install openai anthropic google-generativeai

# ML Libraries
pip install transformers accelerate bitsandbytes

# Development Tools
pip install jupyter notebook ipykernel
pip install black ruff mypy pytest pytest-asyncio

# Create project structure
echo -e "${YELLOW}Creating project directories...${NC}"
mkdir -p {src/{agents,apps,automations,business},tests/{unit,integration},config,data/{raw,processed},notebooks,scripts,docker,deployment,docs,.github/workflows}

# Create .env template
cat > .env.example << 'EOF'
# API Keys - Replace with your actual keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-api-key
GROQ_API_KEY=your-groq-api-key

# Vector Database Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-key
CHROMA_PERSIST_DIR=./data/chromadb

# Model Configuration
OPENAI_MODEL=gpt-5.5
ANTHROPIC_MODEL=claude-opus-4.8
LOCAL_MODEL=qwen3.5:72b

# Application Settings
LOG_LEVEL=INFO
MAX_TOKENS=8192
TEMPERATURE=0.7
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core AI Frameworks
langchain==0.3.15
langchain-community==0.3.15
langchain-openai==0.3.2
langchain-anthropic==0.3.4
llama-index==0.12.8
crewai==0.108.0

# Web Framework
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
pydantic-settings==2.7.1

# Vector Databases
qdrant-client==1.13.0
chromadb==0.6.3

# AI Providers
openai==1.58.1
anthropic==0.49.0
google-generativeai==0.8.4

# Machine Learning
torch>=2.5.0
transformers==4.48.3
accelerate==1.3.0
bitsandbytes==0.45.2

# Development Tools
python-dotenv==1.0.1
jupyter==1.1.1
ipykernel==6.29.5
black==24.10.0
ruff==0.8.6
mypy==1.14.1
pytest==8.3.4
pytest-asyncio==0.25.0

# Utilities
httpx==0.28.1
aiohttp==3.11.11
tqdm==4.67.1
rich==13.9.4
EOF

echo -e "${GREEN}✓ macOS environment setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit .env.example to add your API keys and rename to .env"
echo "2. Activate environment: conda activate ai_projects"
echo "3. Start building: cd src && python your_project.py"
```

#### Linux Setup Script

Create `setup_linux.sh`:

```bash
#!/bin/bash
# Linux AI Project Environment Setup Script
# Requires: Ubuntu 22.04+/Debian 12+, sudo privileges

set -e

echo "========================================"
echo "  AI Project Environment Setup (Linux)"
echo "========================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Update system packages
echo -e "${YELLOW}Updating system packages...${NC}"
sudo apt-get update && sudo apt-get upgrade -y

# Install system dependencies
echo -e "${YELLOW}Installing system dependencies...${NC}"
sudo apt-get install -y \
    python3.12 python3.12-dev python3.12-venv \
    build-essential libssl-dev libffi-dev \
    wget curl git \
    nvidia-cuda-toolkit \
    docker.io docker-compose-v2 \
    postgresql-client

# Install Miniconda
if ! command -v conda &> /dev/null; then
    echo -e "${YELLOW}Installing Miniconda...${NC}"
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
    bash ~/miniconda.sh -b -p $HOME/miniconda
    eval "$($HOME/miniconda/bin/conda shell.bash hook)"
    conda init
fi

# Create conda environment
echo -e "${YELLOW}Creating AI project environment...${NC}"
conda create -n ai_projects python=3.12 -y
conda activate ai_projects

# Install CUDA-enabled PyTorch
echo -e "${YELLOW}Installing CUDA-enabled PyTorch...${NC}"
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Install AI frameworks
echo -e "${YELLOW}Installing AI frameworks...${NC}"
pip install langchain==0.3.15 langchain-community langchain-openai langchain-anthropic
pip install llama-index==0.12.8
pip install crewai==0.108.0

# Install web framework
pip install fastapi uvicorn[standard]
pip install python-dotenv pydantic pydantic-settings

# Install vector databases
pip install qdrant-client chromadb

# Install AI providers
pip install openai anthropic google-generativeai

# Install ML libraries
pip install transformers accelerate bitsandbytes

# Install development tools
pip install jupyter notebook ipykernel
pip install black ruff mypy pytest pytest-asyncio

# Create project structure
echo -e "${YELLOW}Creating project directories...${NC}"
mkdir -p {src/{agents,apps,automations,business},tests/{unit,integration},config,data/{raw,processed},notebooks,scripts,docker,deployment,docs,.github/workflows}

# Create .env template
cat > .env.example << 'EOF'
# API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-api-key
GROQ_API_KEY=your-groq-api-key

# Vector Database Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-key
CHROMA_PERSIST_DIR=./data/chromadb

# Model Configuration
OPENAI_MODEL=gpt-5.5
ANTHROPIC_MODEL=claude-opus-4.8
LOCAL_MODEL=qwen3.5:72b

# Application Settings
LOG_LEVEL=INFO
MAX_TOKENS=8192
TEMPERATURE=0.7
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core AI Frameworks
langchain==0.3.15
langchain-community==0.3.15
langchain-openai==0.3.2
langchain-anthropic==0.3.4
llama-index==0.12.8
crewai==0.108.0

# Web Framework
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
pydantic-settings==2.7.1

# Vector Databases
qdrant-client==1.13.0
chromadb==0.6.3

# AI Providers
openai==1.58.1
anthropic==0.49.0
google-generativeai==0.8.4

# Machine Learning
torch>=2.5.0
transformers==4.48.3
accelerate==1.3.0
bitsandbytes==0.45.2

# Development Tools
python-dotenv==1.0.1
jupyter==1.1.1
ipykernel==6.29.5
black==24.10.0
ruff==0.8.6
mypy==1.14.1
pytest==8.3.4
pytest-asyncio==0.25.0

# Utilities
httpx==0.28.1
aiohttp==3.11.11
tqdm==4.67.1
rich==13.9.4
EOF

echo -e "${GREEN}✓ Linux environment setup complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit .env.example to add your API keys and rename to .env"
echo "2. Activate environment: conda activate ai_projects"
echo "3. Start building: cd src && python your_project.py"
```

### 1.2 API Key Configuration

Create a `.env` file from the template and populate it with your API keys:

```bash
# Copy the template
cp .env.example .env

# Edit the file with your actual API keys
# For security, never commit .env to version control
```

Add `.env` to your `.gitignore`:

```gitignore
# .gitignore
.env
.env.local
*.pyc
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
*.egg-info/
data/raw/
data/processed/
chromadb/
```

## Section 2: Project Configuration Files

### 2.1 Complete requirements.txt

The following `requirements.txt` covers all projects in this book:

```txt
# =============================================================================
# AI Project Mastery 2026 - Complete Requirements
# Python 3.12+ Required
# =============================================================================

# ── Core AI Frameworks ──────────────────────────────────────────────────────
langchain==0.3.15
langchain-community==0.3.15
langchain-openai==0.3.2
langchain-anthropic==0.3.4
langchain-google-genai==0.2.3
langchain-core==0.3.29
langgraph==0.2.60
llama-index==0.12.8
llama-index-embeddings-openai==0.3.1
llama-index-vector-stores-qdrant==0.4.1
crewai==0.108.0
crewai-tools==0.14.0

# ── Web Framework & API ─────────────────────────────────────────────────────
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.4
pydantic-settings==2.7.1
httpx==0.28.1
aiohttp==3.11.11
requests==2.32.3

# ── Vector Databases & Retrieval ────────────────────────────────────────────
qdrant-client==1.13.0
chromadb==0.6.3
pinecone-client==5.0.1
weaviate-client==4.10.1

# ── AI Providers ────────────────────────────────────────────────────────────
openai==1.58.1
anthropic==0.49.0
google-generativeai==0.8.4
groq==0.15.0
together==1.4.2

# ── Machine Learning & Deep Learning ────────────────────────────────────────
torch>=2.5.0
torchvision>=0.20.0
torchaudio>=2.5.0
transformers==4.48.3
accelerate==1.3.0
bitsandbytes==0.45.2
sentence-transformers==3.3.1
tiktoken==0.8.0

# ── Data Processing ─────────────────────────────────────────────────────────
pandas==2.2.3
numpy==1.26.4
pypdf==5.1.0
python-docx==1.1.2
unstructured==0.16.12
beautifulsoup4==4.12.3
lxml==5.3.0

# ── Development & Testing ───────────────────────────────────────────────────
python-dotenv==1.0.1
jupyter==1.1.1
ipykernel==6.29.5
black==24.10.0
ruff==0.8.6
mypy==1.14.1
pytest==8.3.4
pytest-asyncio==0.25.0
pytest-cov==6.0.0

# ── Monitoring & Logging ────────────────────────────────────────────────────
loguru==0.7.3
tqdm==4.67.1
rich==13.9.4
wandb==0.19.1

# ── Deployment & Infrastructure ─────────────────────────────────────────────
docker==7.1.0
redis==5.2.1
celery==5.4.0
sqlalchemy==2.0.36
asyncpg==0.30.0
alembic==1.14.0
```

### 2.2 pyproject.toml Template

For modern Python projects using Poetry or pip, use this `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel>=0.41.0"]
build-backend = "setuptools.build_meta"

[project]
name = "ai-project-mastery"
version = "1.0.0"
description = "AI Project Mastery 2026 - Build Agents, Apps, Automations, and Businesses"
readme = "README.md"
requires-python = ">=3.12"
license = {text = "MIT"}
authors = [
    {name = "AI Project Mastery", email = "author@aiprojectmastery.com"}
]

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

dependencies = [
    "langchain==0.3.15",
    "langchain-community==0.3.15",
    "langchain-openai==0.3.2",
    "langchain-anthropic==0.3.4",
    "langgraph==0.2.60",
    "llama-index==0.12.8",
    "crewai==0.108.0",
    "fastapi==0.115.6",
    "uvicorn[standard]==0.34.0",
    "pydantic==2.10.4",
    "pydantic-settings==2.7.1",
    "qdrant-client==1.13.0",
    "chromadb==0.6.3",
    "openai==1.58.1",
    "anthropic==0.49.0",
    "google-generativeai==0.8.4",
    "torch>=2.5.0",
    "transformers==4.48.3",
    "accelerate==1.3.0",
    "python-dotenv==1.0.1",
    "httpx==0.28.1",
    "pandas==2.2.3",
    "tqdm==4.67.1",
    "rich==13.9.4",
]

[project.optional-dependencies]
dev = [
    "black==24.10.0",
    "ruff==0.8.6",
    "mypy==1.14.1",
    "pytest==8.3.4",
    "pytest-asyncio==0.25.0",
    "jupyter==1.1.1",
    "ipykernel==6.29.5",
]
gpu = [
    "bitsandbytes==0.45.2",
    "sentence-transformers==3.3.1",
]
deploy = [
    "docker==7.1.0",
    "redis==5.2.1",
    "celery==5.4.0",
    "sqlalchemy==2.0.36",
]

[tool.black]
line-length = 100
target-version = ["py312"]

[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true
warn_unused_ignores = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
asyncio_mode = "auto"

[project.scripts]
run-agent = "src.agents.main:run"
run-app = "src.apps.main:run"
run-automation = "src.automations.main:run"
```

## Section 3: Docker Compose Files for Self-Hosted Tools

### 3.1 Complete Docker Compose Configuration

Create `docker/docker-compose.yml`:

```yaml
version: '3.8'

services:
  # ── Ollama - Local LLM Inference ──────────────────────────────────────
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama_data:/root/.ollama
      - ./models:/models
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_KEEP_ALIVE=24h
      - OLLAMA_NUM_PARALLEL=4
      - OLLAMA_MAX_LOADED_MODELS=2
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    networks:
      - ai_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ── Open WebUI - Chat Interface for Ollama ────────────────────────────
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    volumes:
      - open_webui_data:/app/backend/data
    ports:
      - "3000:8080"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY:-change-me-in-production}
      - WEBUI_NAME=AI Project Mastery
      - ENABLE_SIGNUP=false
      - DEFAULT_MODELS=qwen3.5:72b
    depends_on:
      ollama:
        condition: service_healthy
    networks:
      - ai_network
    restart: unless-stopped

  # ── Qdrant - Vector Database ──────────────────────────────────────────
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    volumes:
      - qdrant_data:/qdrant/storage
      - qdrant_config:/qdrant/config
    ports:
      - "6333:6333"
      - "6334:6334"
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
      - QDRANT__SERVICE__API_KEY=${QDRANT_API_KEY:-}
      - QDRANT__LOG_LEVEL=INFO
    networks:
      - ai_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ── n8n - Workflow Automation ─────────────────────────────────────────
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n/backups:/backups
      - ./n8n/credentials:/credentials
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD:-change-me}
      - N8N_HOST=${N8N_HOST:-localhost}
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - NODE_ENV=production
      - WEBHOOK_URL=${WEBHOOK_URL:-http://localhost:5678}
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168
    networks:
      - ai_network
    restart: unless-stopped
    depends_on:
      - qdrant
      - ollama

  # ── Redis - Caching & Message Broker ──────────────────────────────────
  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis-pass}
    networks:
      - ai_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ── PostgreSQL - Relational Database ──────────────────────────────────
  postgres:
    image: postgres:16-alpine
    container_name: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=ai_projects
      - POSTGRES_USER=${POSTGRES_USER:-ai_user}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-change-me}
    networks:
      - ai_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ai_user -d ai_projects"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ── Jupyter Lab - Development Environment ─────────────────────────────
  jupyter:
    image: jupyter/datascience-notebook:latest
    container_name: jupyter
    volumes:
      - ../:/home/jovyan/work
      - jupyter_data:/home/jovyan/.jupyter
    ports:
      - "8888:8888"
    environment:
      - JUPYTER_ENABLE_LAB=yes
      - JUPYTER_TOKEN=${JUPYTER_TOKEN:-ai-project-mastery}
    networks:
      - ai_network
    restart: unless-stopped

  # ── Traefik - Reverse Proxy (Optional) ─────────────────────────────────
  traefik:
    image: traefik:v3.0
    container_name: traefik
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=${LETSENCRYPT_EMAIL:-admin@example.com}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - traefik_data:/letsencrypt
    networks:
      - ai_network
    restart: unless-stopped

volumes:
  ollama_data:
  open_webui_data:
  qdrant_data:
  qdrant_config:
  n8n_data:
  redis_data:
  postgres_data:
  jupyter_data:
  traefik_data:

networks:
  ai_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 3.2 Docker Compose for Production

Create `docker/docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Production-grade configuration with resource limits and logging
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    deploy:
      resources:
        limits:
          memory: 16G
        reservations:
          memory: 8G
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    depends_on:
      - ollama
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
      - ENABLE_SIGNUP=false
    volumes:
      - open_webui_data:/app/backend/data
    ports:
      - "3000:8080"
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"

  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=${POSTGRES_USER}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - WEBHOOK_URL=${N8N_WEBHOOK_URL}
    volumes:
      - n8n_data:/home/node/.n8n
    ports:
      - "5678:5678"
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: postgres
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  ollama_data:
  open_webui_data:
  n8n_data:
  postgres_data:
```

Deploy with:

```bash
# Copy and configure environment variables
cp .env.example .env
# Edit .env with your values

# Pull all images and start services
docker compose -f docker/docker-compose.prod.yml up -d

# Verify all containers are running
docker compose -f docker/docker-compose.prod.yml ps

# Pull your first model
docker exec ollama ollama pull llama4
```

---

## Section 4: Deployment Guides

### 4.1 Vercel (Next.js frontend)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from project root
vercel

# Set environment variables
vercel env add NEXT_PUBLIC_SUPABASE_URL
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
vercel env add ANTHROPIC_API_KEY

# Deploy to production
vercel --prod
```

### 4.2 Railway (FastAPI backend)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialise
railway login
railway init

# Add environment variables
railway variables set ANTHROPIC_API_KEY=your_key
railway variables set DATABASE_URL=your_db_url

# Deploy
railway up
```

### 4.3 DigitalOcean Droplet (self-hosted n8n + Ollama)

```bash
# Provision a droplet (8GB RAM minimum for LLMs)
# Ubuntu 22.04, 8GB/4vCPU recommended

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Clone your project
git clone https://github.com/your-username/your-project.git
cd your-project

# Configure and start
cp .env.example .env && nano .env
docker compose -f docker/docker-compose.prod.yml up -d
```

---

## Section 5: Troubleshooting FAQ

### Q: `CUDA out of memory` when running Ollama

**Cause**: Model is too large for your GPU VRAM.

**Fix**: Use a quantised variant:
```bash
ollama pull llama4:8b-q4_K_M   # 4-bit quantised — fits in 8GB VRAM
```

### Q: n8n webhook not receiving events from external services

**Cause**: `WEBHOOK_URL` is set to `localhost`, which is unreachable from the internet.

**Fix**: Set `WEBHOOK_URL` to your public server IP or domain:
```bash
WEBHOOK_URL=https://your-server.com
```

### Q: Supabase RLS blocking API requests

**Cause**: Row Level Security policies are enabled but no policy matches the request.

**Fix**: In Supabase dashboard → Authentication → Policies, add a policy for your table:
```sql
CREATE POLICY "Allow authenticated reads"
ON public.your_table
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);
```

### Q: `ModuleNotFoundError` when running Python scripts

**Cause**: Virtual environment is not activated, or dependencies are missing.

**Fix**:
```bash
source venv/bin/activate   # Linux/macOS
# or
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### Q: DOCX file not rendering images in Amazon KDP preview

**Cause**: Image paths in the markdown use bare filenames without the `images/` prefix.

**Fix**: Run the image reference fixer:
```bash
python scripts/fix_image_refs.py projects/ai-project-mastery-v2
```

---

## Summary

This appendix gives you everything you need to go from a local development environment to a production deployment for any project in this book. The Docker Compose configuration handles the full self-hosted AI stack. The deployment guides cover the three most common hosting targets. The troubleshooting FAQ addresses the errors you are most likely to encounter.

Clone the companion repository, follow the setup script for your operating system, and you will have a working environment within fifteen minutes on any machine.
