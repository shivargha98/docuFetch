# PM Loop Context

**Scope:** backend
**Feature:** docuFetch — personal RAG backend
**Date:** 2026-06-30

## Important Decisions

### Architecture Decisions (from grill_doc_roadmap.md)
- Image handling: Direct vision embedding via OpenRouter VL model (no OCR)
- Image storage in ChromaDB: File path in metadata only; image reloaded at query time
- Chunking: Structure-aware — MarkdownHeaderTextSplitter for .md, RecursiveCharacterTextSplitter (512 chars, 64 overlap) for PDF/TXT, single chunk per image
- Hybrid retrieval: BM25 + ChromaDB vector similarity fused via RRF (EnsembleRetriever), top-5 each → top-3 final
- Change detection: SHA256 hash-based, JSON state file (hash_store.json)
- Scheduler: asyncio background task, 60s interval, runs once at startup via FastAPI lifespan
- RAG framework: LangGraph (not LCEL) — enables conditional routing for relevance check
- Multi-turn chat: In-memory per session, UUID-keyed, capped at 20 messages, lost on restart
- Relevance check: LLM-judged (Claude Haiku yes/no), conditional edge to generate or no_results node
- LLM API: Anthropic SDK directly (ChatAnthropic); OpenRouter used only for embeddings
- Endpoints: POST /chat, GET /health, POST /ingest, GET /ingest/status
- CLI: Separate cli.py using httpx, UUID session on startup, /ingest /status /quit commands
- Retrieval N/K: N=5 per retriever, K=3 final after RRF
- Session management: Client-generated UUID, in-memory dict, no /session endpoint
- Source citation: Filename only (e.g. [source: policy.pdf])

## Key Outputs by Stage

### PRD
- **Core problem:** No way to ask natural language questions across a personal document collection (PDFs, Markdown, TXT, images) without manually opening files.
- **Primary user goals:** Auto-ingest watched folder, answer questions with 2–4 sentence responses citing source filenames, explicitly say when nothing is found.
- **Key constraints:** Local-first (ChromaDB on disk), session history in-memory only (lost on restart), filename-only citations, 20-message history cap per session.
- **Out of scope:** Frontend UI, auth, persistent sessions, file types beyond PDF/MD/TXT/JPEG/JPG/PNG, page-level citations.

### Features
- **Total features:** 17
- **Modules covered:** Ingestion (3), Embeddings (2), Retrieval (2), Graph (5), API (5), CLI (1)
- **All 21 user stories map to at least one feature.** No orphaned stories.
- **Notable decisions:**
  - File Change Detection is a standalone feature (not bundled with loaders) — cleaner testability
  - LangGraph state schema is its own feature because it's the contract all nodes depend on
  - Graph Assembly is separate from individual nodes — allows nodes to be tested in isolation first
  - POST /ingest is sync-or-immediate (not deferred to next 60s tick) — important for CLI UX
  - CLI connection error handling is an explicit acceptance criterion (not assumed)

### Issues
- **Total issues:** 9, written in dependency order (blockers first)
- **Dependency chain:** 1 → 2 → {3, 4, 5, 6} → 7 → 8 → 9
- **Issue 1:** Scaffold + /health (foundation)
- **Issue 2:** TXT/PDF ingestion + embedding + ChromaDB + POST /ingest + GET /ingest/status (proves full path)
- **Issue 3:** Markdown ingestion (extends Issue 2)
- **Issue 4:** Image ingestion with VL embedding (extends Issue 2)
- **Issue 5:** Hash-based change detection + startup scheduler (extends Issue 2)
- **Issue 6:** BM25 + hybrid retrieval with RRF (extends Issue 2)
- **Issue 7:** LangGraph pipeline — retrieve, relevance check, generate, no-results (extends Issue 6)
- **Issue 8:** POST /chat endpoint + multi-turn session management (extends Issue 7)
- **Issue 9:** CLI client (extends Issues 5 + 8)
- **Coverage check:** All 17 features from features.md are covered. No orphaned features.
- **Notable slicing decisions:**
  - Issues 3 and 4 (Markdown, image ingestion) are separate from Issue 2 (TXT/PDF) — each adds a new file type with a distinct loading/chunking strategy
  - GET /health update (initial_ingestion_complete) is deferred to Issue 5 (scheduler) where the flag becomes meaningful
  - LangGraph pipeline is one issue (7) rather than one issue per node — assembly is tightly coupled and testing individual nodes without the graph is not meaningful at this scale

### Test Suite
- **Total tests:** 54 (21 unit, 19 integration, 14 API)
- **Stub files:** backend/tests/conftest.py, unit/ (5 files), integration/ (4 files), api/ (1 file)
- **Coverage by module:**
  - Scanner: 5 unit tests
  - Loaders: 5 unit tests
  - Chunkers: 6 unit tests
  - Retrieval (unit): 2 unit tests
  - Graph nodes (unit): 4 unit tests
  - CLI (unit): 3 unit tests
  - ChromaDB store: 4 integration tests
  - Ingestion pipeline: 5 integration tests
  - Hybrid retrieval: 4 integration tests
  - RAG pipeline: 4 integration tests
  - GET /health: 3 API tests
  - POST /ingest: 2 API tests
  - GET /ingest/status: 4 API tests
  - POST /chat: 5 API tests
- **Test types generated:** unit (isolated, no external services), integration (real ChromaDB + real embedding/LLM APIs), API (FastAPI TestClient)
- **No mock policy:** ChromaDB and LangGraph are tested against real instances; only the httpx client is mocked in CLI unit tests
- **Gaps flagged:** None — all 17 features and all 21 user stories have at least one test mapping

## Open Questions / Risks
- BM25 index is rebuilt in-memory at startup — may be slow for very large document sets
- Image path storage assumes watched folder path is stable (files won't move)
- In-memory session history is lost on server restart (acceptable for personal use)

## Build Decisions (Orchestrator Round)

### Fixes surfaced by integration worker (Round 6)
- `claude-3-5-haiku-20241022` is end-of-life. Updated to `claude-haiku-4-5` in `backend/api/server.py`. This must be kept current with Anthropic model lifecycle.
- `embed_image()` input format: OpenRouter's VL endpoint requires a plain base64 data URI string, not an `{"type":"image_url","image_url":{"url":...}}` dict. Worker corrected this.
- TestClient lifespan: all API tests must use `with TestClient(app) as client:` — not doing so silently skips lifespan startup, causing AttributeError on `app.state.*`.
- conftest skip markers: integration/API tests skip (not fail) when API keys are not present. Pattern: `skip_if_no_openrouter` / `skip_if_no_anthropic` defined in conftest.py.

### Final test result
56 passed, 0 failed, 0 skipped — 2026-06-30

## Loop Completion Summary
**Status:** Complete
**Total features:** 17 (across 6 modules: Ingestion, Embeddings, Retrieval, Graph, API, CLI)
**Total issues:** 9 (dependency order: 1 → 2 → {3,4,5,6} → 7 → 8 → 9)
**Test coverage:** 54 tests (21 unit, 19 integration, 14 API), all 17 features covered, all 21 user stories covered
**Key decisions made:**
- LangGraph chosen over LCEL from the start (enables conditional routing for relevance check node)
- LangGraph pipeline kept as one issue (7) rather than per-node issues — nodes are tightly coupled through shared state
- Image chunks excluded from BM25, participate in vector search only
- GET /health `initial_ingestion_complete` flag deferred to Issue 5 (scheduler) where it becomes meaningful
- POST /ingest (Issue 2) is a one-shot manual trigger; automated polling is wired in Issue 5
- Test suite uses real ChromaDB and real LLM/embedding APIs for integration tests — no mocking of external services in integration layer
- CLI httpx calls are the only place where mocking is appropriate (unit tests for session_id reuse, error handling)
**Risks or open questions remaining:**
- Integration and API tests require live ANTHROPIC_API_KEY and OPENROUTER_API_KEY — test environment setup not yet defined
- BM25 startup latency at scale is an open risk (acceptable for personal use, not benchmarked)
- No `conftest.py` fixtures are implemented yet — developer must fill them in before running tests
