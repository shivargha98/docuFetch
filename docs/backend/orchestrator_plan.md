# Orchestrator Plan — docuFetch Backend

_Written: 2026-06-30 | Owner: backend orchestrator_

---

## Source of Truth

All work is driven from `docs/backend/issues.md`. 9 issues total, written in dependency order. Features in `features.md` and PRD in `prd.md` are fallback context only.

---

## Dependency Map

```
Issue 1 (Scaffold)
    └── Issue 2 (TXT/PDF Ingestion + /ingest + /ingest/status)
            ├── Issue 3 (Markdown Ingestion)       ─┐
            ├── Issue 4 (Image Ingestion)            │ Round 3
            ├── Issue 5 (Scanner + Scheduler)        │ (see parallelization below)
            └── Issue 6 (BM25 + Hybrid Retrieval)  ─┘
                    └── Issue 7 (LangGraph RAG Pipeline)
                                └── Issue 8 (POST /chat)
                                            │
                    Issue 5 ───────────────┘
                                            └── Issue 9 (CLI)
```

---

## Build Rounds

### Round 1 — Foundation
| Issue | Worker | Parallel | Rationale |
|-------|--------|----------|-----------|
| 1 | worker-scaffold | alone | Creates all directories and the health endpoint. Every subsequent issue depends on it. |

### Round 2 — First Vertical Slice
| Issue | Worker | Parallel | Rationale |
|-------|--------|----------|-----------|
| 2 | worker-ingestion-core | alone | Proves full ingest-to-store path (TXT/PDF → embed → ChromaDB). All Round 3 issues extend from here. |

### Round 3a — Parallel Extensions (safe: no shared-file conflicts)
| Issue | Worker | Files touched |
|-------|--------|---------------|
| 3 | worker-markdown-ingestion | `backend/ingestion/loaders.py`, `backend/ingestion/chunkers.py` |
| 5 | worker-scheduler | `backend/ingestion/scanner.py` (new), `backend/api/server.py` (lifespan + health flag) |
| 6 | worker-retrieval | `backend/retrieval/bm25.py` (new), `backend/retrieval/hybrid.py` (new) |

Issues 3, 5, 6 touch distinct files — safe to run in parallel.

### Round 3b — Next Parallel Batch (after Round 3a)
| Issue | Worker | Dependency reason |
|-------|--------|-------------------|
| 4 | worker-image-ingestion | Extends `loaders.py` + `chunkers.py` which Issue 3 also modifies — Issue 3 must finish first |
| 7 | worker-rag-pipeline | Depends on hybrid retrieval from Issue 6 (done in Round 3a) |

Issues 4 and 7 touch entirely different files — safe to run in parallel within Round 3b.

### Round 4 — Chat Endpoint
| Issue | Worker | Rationale |
|-------|--------|-----------|
| 8 | worker-chat-endpoint | Extends `backend/api/routes.py` with POST /chat, wires in LangGraph pipeline from Issue 7 |

### Round 5 — CLI
| Issue | Worker | Rationale |
|-------|--------|-----------|
| 9 | worker-cli | Depends on Issue 5 (scheduler state) and Issue 8 (POST /chat). All server features stable. |

### Round 6 — Integration
- Integration worker copies test stubs from `docs/backend/tests/` to `backend/tests/`, implements all fixtures and test bodies, and runs the full test suite.

---

## File Structure (canonical — from grill_doc_roadmap.md)

```
/workspace/
├── server.py              ← thin shim: from backend.api.server import app
├── cli.py                 ← standalone CLI (httpx)
├── requirements.txt       ← all dependencies
├── .env.example           ← env var template
├── backend/
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── scanner.py     ← Issue 5
│   │   ├── loaders.py     ← Issue 2 (TXT/PDF), extended in Issue 3 (MD), Issue 4 (image)
│   │   └── chunkers.py    ← Issue 2 (TXT/PDF), extended in Issue 3 (MD), Issue 4 (image)
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── embedder.py    ← Issue 2
│   │   └── store.py       ← Issue 2
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── bm25.py        ← Issue 6
│   │   └── hybrid.py      ← Issue 6
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py       ← Issue 7
│   │   ├── nodes.py       ← Issue 7
│   │   └── graph.py       ← Issue 7
│   └── api/
│       ├── __init__.py
│       ├── server.py      ← Issue 1 (skeleton), updated in Issue 5 (lifespan)
│       └── routes.py      ← Issue 2 (/ingest, /ingest/status), Issue 8 (/chat)
└── backend/tests/         ← test implementations (Round 6 integration)
    ├── conftest.py
    ├── unit/
    ├── integration/
    └── api/
```

---

## Risk Notes

1. **loaders.py / chunkers.py shared-file conflict**: Issues 3, 4 both extend these files. Strictly serialized: Issue 3 in Round 3a, Issue 4 in Round 3b. Worker briefs must show exact function signatures to prevent interface drift.

2. **server.py (root) vs backend/api/server.py**: The CLAUDE.md run command is `uvicorn server:app`. Issue 1 worker must create a root `server.py` shim that imports `app` from `backend.api.server`. All subsequent workers treat `backend/api/server.py` as canonical.

3. **requirements.txt completeness**: Issue 1 worker writes the full requirements.txt upfront. All workers install from this file — no worker should add new packages without updating requirements.txt.

4. **Integration tests require live API keys**: `OPENROUTER_API_KEY` and `ANTHROPIC_API_KEY` must be present in the test environment. Integration worker must check for these and skip gracefully if absent.

5. **Test stub location**: Stubs live in `docs/backend/tests/` (planning artifacts). Real test implementations go into `backend/tests/`. Integration worker handles this copy-and-implement step.

6. **BM25 at startup**: The hybrid retriever builds a BM25 index from all stored text chunks at startup. Issue 6 must expose a `rebuild_bm25_index()` function that Issue 5's scheduler calls after each ingestion run.

---

## Decisions Log

| Decision | Rationale |
|----------|-----------|
| Issue 4 deferred to Round 3b | Issues 3 and 4 both modify loaders.py and chunkers.py — conflict prevented by serializing them |
| Issue 7 in Round 3b alongside Issue 4 | Issue 7 only depends on Issue 6 (done in Round 3a); its graph/ files don't conflict with ingestion/ |
| Root server.py shim | CLAUDE.md requires `uvicorn server:app`; canonical app lives in `backend/api/server.py` |
| Full requirements.txt in Round 1 | All packages known upfront; avoids repeated installs and version conflicts |
