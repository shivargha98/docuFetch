# Worker Brief — Issue 1: FastAPI Project Scaffold with Health Endpoint

**Working directory:** `/workspace`
**Issue:** Issue 1 (from docs/backend/issues.md)
**Your report goes to:** `docs/backend/agent-reports/worker-scaffold-report.md`

---

## What to Build

Create the complete project scaffold for the docuFetch backend. This is the foundation — it must be done correctly because every subsequent worker builds on it.

Specifically:
1. Full directory structure for the backend
2. `requirements.txt` with all packages the entire backend will need (not just Issue 1)
3. A `.env.example` file documenting all required environment variables
4. `backend/api/server.py` — the FastAPI application with one live endpoint: `GET /health`
5. `server.py` at the project root — a thin shim that imports `app` from `backend.api.server`
6. All `__init__.py` files for every package

---

## Directory Structure to Create

```
/workspace/
├── server.py                    ← shim: from backend.api.server import app
├── requirements.txt             ← FULL dependency list (see below)
├── .env.example                 ← all env vars documented
├── backend/
│   ├── __init__.py
│   ├── ingestion/
│   │   └── __init__.py
│   ├── embeddings/
│   │   └── __init__.py
│   ├── retrieval/
│   │   └── __init__.py
│   ├── graph/
│   │   └── __init__.py
│   └── api/
│       ├── __init__.py
│       ├── server.py            ← FastAPI app, health endpoint
│       └── routes.py            ← empty for now (stub that future workers will extend)
```

Do NOT create scanner.py, loaders.py, chunkers.py, embedder.py, store.py, bm25.py, hybrid.py, state.py, nodes.py, graph.py, or cli.py — those belong to later issues.

---

## requirements.txt

Write the FULL requirements.txt (all packages the entire project will eventually need). Later workers should not need to add packages. Include:

```
fastapi
uvicorn[standard]
python-dotenv
pdfplumber
pillow
langchain
langchain-anthropic
langchain-community
langgraph
chromadb
rank-bm25
httpx
fpdf2
pytest
pytest-asyncio
openai
```

Note: `openai` is needed because OpenRouter uses an OpenAI-compatible API. `fpdf2` is for creating test PDF fixtures. `rank-bm25` is the BM25 implementation. Do not pin versions unless you have a specific reason.

---

## .env.example

```
WATCH_FOLDER=/path/to/your/documents
OPENROUTER_API_KEY=your_openrouter_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
CHROMA_DB_PATH=./chroma_db
HASH_STORE_PATH=./hash_store.json
```

---

## backend/api/server.py

The FastAPI application. Requirements:
- `app = FastAPI(title="docuFetch")` at module level (must be importable as `from backend.api.server import app`)
- `app.state.initial_ingestion_complete = False` — set on startup, updated later by Issue 5's scheduler
- `app.state.sessions = {}` — placeholder for Issue 8's session management
- Import and include routes from `backend.api.routes` (even though routes.py starts mostly empty)
- `GET /health` endpoint returning `{"status": "ok", "initial_ingestion_complete": bool}`
- Load environment variables from `.env` using `python-dotenv` at module level
- File description comment at the top explaining what the file does
- Every function must have a docstring

The health endpoint:
```python
@app.get("/health")
def health():
    """Returns server status and whether initial ingestion has completed."""
    return {
        "status": "ok",
        "initial_ingestion_complete": app.state.initial_ingestion_complete
    }
```

Note: `initial_ingestion_complete` will be set to True by the scheduler in Issue 5. For now it is always False.

---

## backend/api/routes.py

An empty-but-valid stub for now. It should just have a router object so `server.py` can include it without error:

```python
from fastapi import APIRouter
router = APIRouter()
```

And `server.py` does: `app.include_router(router)` — this means when Issue 2 adds routes to routes.py, they will automatically appear on the server.

---

## server.py (root shim)

```python
"""
Entry point shim for uvicorn.

Imports the FastAPI app from the backend package so the server can be started
with: uvicorn server:app --port 8000 --reload
"""
from backend.api.server import app  # noqa: F401
```

That's it. Do not add logic here.

---

## Coding Standards (enforce for all files you create)

- Every file must have a module-level docstring at the top describing what the code in the file does
- Every function must have a docstring
- Simplicity first — no speculative features, no abstractions beyond what's needed right now
- Match the style of this brief's examples exactly

---

## Acceptance Criteria (verify before reporting done)

- [ ] `GET /health` returns HTTP 200 with `{ "status": "ok", "initial_ingestion_complete": false }`
- [ ] The FastAPI app starts with `uvicorn server:app --port 8000 --reload` without errors (test this)
- [ ] All required packages listed above are in `requirements.txt`
- [ ] `.env.example` documents all 5 env vars: `WATCH_FOLDER`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `CHROMA_DB_PATH`, `HASH_STORE_PATH`
- [ ] The `backend/` directory structure exists with all `__init__.py` files

## How to verify the server starts

Install dependencies first:
```bash
cd /workspace
pip install -r requirements.txt
```

Then test the server starts:
```bash
cd /workspace
uvicorn server:app --port 8000 --reload &
sleep 3
curl -s http://localhost:8000/health
kill %1
```

Expected output: `{"status":"ok","initial_ingestion_complete":false}`

---

## What to Write in Your Report

Write `docs/backend/agent-reports/worker-scaffold-report.md` with:
1. Status: DONE or FAILED
2. Files created (list every file)
3. Verification output (paste the curl response)
4. Any deviations from this brief and why
5. Anything Issue 2 worker needs to know about the interfaces you established (e.g., how routes.py is structured, what app.state holds)
