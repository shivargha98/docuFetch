# docuFetch

A personal RAG (Retrieval-Augmented Generation) application. Point it at a folder of documents, ask questions in a chat interface, and get concise answers with source citations — all running locally.

## What it does

- Watches a local folder and ingests documents (text, markdown, images) on a schedule
- Chunks and embeds each file into a local ChromaDB vector store
- Accepts natural-language queries through a web chat UI
- Retrieves the top relevant chunks, generates a 2–4 sentence answer via Claude, and cites the source filename
- Says so explicitly when no relevant document is found

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Vector store | ChromaDB (local) |
| Embeddings | OpenRouter (nvidia/llama-nemotron-embed-vl) |
| LLM | Claude (Anthropic) via `langchain-anthropic` |
| Frontend | React, Tailwind CSS, Vite |

## Running the app

**1. Install backend dependencies**

```bash
pip install -r requirements.txt
```

**2. Set environment variables**

Copy `.env.example` to `.env` and fill in your keys:

```
ANTHROPIC_API_KEY=...
OPENROUTER_API_KEY=...
ANTHROPIC_MODEL=claude-haiku-4-5
OPENROUTER_EMBED_MODEL=nvidia/llama-nemotron-embed-vl-1b-v2:free
WATCH_DIR=./my-documents
```

**3. Start the backend**

```bash
uvicorn server:app --port 8000 --reload --reload-dir backend
```

**4. Start the frontend**

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` — the backend must be running for the chat to work.

---

## How this project was built

docuFetch was built entirely using [Claude Code](https://claude.ai/code) with a two-agent system defined in `.claude/agents/`. Every feature went through the same loop: plan → build → test.

### pm-loop agent

The PM loop agent runs the full product management lifecycle from a single sentence description. You tell it what you want to build, and it produces four structured documents in sequence — each one feeding the next:

```
"Build a document ingestion pipeline"
        ↓
   prd.md          ← product requirements document
        ↓
   features.md     ← full feature list extracted from the PRD
        ↓
   issues.md       ← granular implementation issues from each feature
        ↓
   tests.md        ← complete test plan covering every issue
```

It maintains a `context.md` and `tasks.md` throughout, recording every decision it makes. The output of one run becomes the input for the orchestrator.

### orchestrator agent

The orchestrator takes the documents produced by the PM loop and manages the actual build. It never writes code itself — its job is to read, plan, delegate, and synthesize.

```
issues.md  →  dependency map  →  parallel build batches
                                         ↓
                             worker-[feature]-brief.md   (one per issue)
                                         ↓
                             worker agents  (one per brief, run in parallel)
                                         ↓
                             worker-[feature]-report.md  (results + interfaces)
                                         ↓
                             next batch  (using prior reports as context)
                                         ↓
                             integration worker  →  full test suite  →  SHIPPED ✓
```

It tracks every issue in `backend_TASKS.md` / `frontend_TASKS.md` and logs all architectural decisions to `backend_context.md` / `frontend_context.md` so that context carries across sessions.

The combination meant the entire backend (10 workers) and frontend (9 workers) were planned, built, tested, and integrated without manually writing a single implementation file.
