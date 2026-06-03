# AI Project Mastery 2026 — Companion Code

Official source code for **_AI Project Mastery 2026: Build Agents, Apps, Automations, and Businesses with the Latest LLMs_** by **Alex Nalin**.

Every code sample from the book, organized by chapter, ready to clone and run.

```
git clone https://github.com/Alex-Nalin/ai-project-mastery-2026.git
cd ai-project-mastery-2026
```

## 📚 Repository structure

| Folder | Chapter |
|--------|---------|
| `chapter-01/` | The 2026 AI Landscape: From Chatbots to Autonomous Agents |
| `chapter-02/` | Prompt Engineering and Reasoning: Chain-of-Thought, MCP, Structured Outputs |
| `chapter-03/` | Agentic AI: Multi-Agent Systems with CrewAI, LangGraph, and n8n |
| `chapter-04/` | AI-Powered Coding: Cursor, GitHub Copilot, and Building Full Apps |
| `chapter-05/` | AI Image, Video, and Voice |
| `chapter-06/` | Local AI and Edge Deployment: Ollama, Open WebUI, 1-Bit LLMs |
| `chapter-07/` | RAG 2.0 and Knowledge Systems: LangChain, LlamaIndex, MCP, NotebookLM |
| `chapter-08/` | AI Automation at Scale: n8n, Zapier, Make |
| `chapter-09/` | AI Business: Products, SaaS, Agencies, Monetizing AI Skills |
| `chapter-10/` | The Future of AI: AGI, Autonomous Agents, Neuro-Symbolic AI |

Each chapter folder has its own `README.md` listing its files.

## 🚀 Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then add your own API keys
```

Run any sample, e.g.:

```bash
python chapter-01/comparator.py
```

## 🔑 API keys

The projects use various AI providers. Copy `.env.example` to `.env` and fill in only the keys you need (see each chapter's README). **Never commit your `.env`** — it is gitignored.

## 🛠️ Versions & updates

The 2026 AI landscape moves fast. Model names, pricing, and SDK signatures change often. This repo is updated as APIs evolve — check **[Releases](../../releases)** for the version matching your printed edition, and **[`CHANGELOG.md`](CHANGELOG.md)** / **[`ERRATA.md`](ERRATA.md)** for corrections.

Found a bug or an outdated dependency? **[Open an issue](../../issues)** — it helps every reader.

## 📄 License

Code samples are released under the [MIT License](LICENSE). The book's text and figures are © Alex Nalin and are **not** covered by this license.
