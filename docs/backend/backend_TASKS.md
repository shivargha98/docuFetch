# Backend Tasks Tracker

_Owner: backend orchestrator | Started: 2026-06-30_

---

## Status Key
- `PENDING` — not yet started
- `IN-PROGRESS` — worker launched
- `DONE` — worker reported success
- `FAILED` — worker reported failure or blocker
- `BLOCKED` — waiting on dependency

---

## Issue Tracker

| Issue | Title | Status | Round | Worker Name | Launched | Completed | Notes |
|-------|-------|--------|-------|-------------|----------|-----------|-------|
| 1 | FastAPI Scaffold + Health Endpoint | DONE | 1 | worker-scaffold | 2026-06-30 | 2026-06-30 | Health endpoint verified; pip bootstrapped --user |
| 2 | TXT+PDF Ingestion + /ingest + /ingest/status | DONE | 2 | worker-ingestion-core | 2026-06-30 | 2026-06-30 | All 5 AC verified live. encoding_format=float fix. |
| 3 | Markdown Ingestion | DONE | 3a | worker-markdown-ingestion | 2026-06-30 | 2026-06-30 | chunk_md splits at headers, file_type="markdown" |
| 4 | Image Ingestion | DONE | 3b | worker-image-ingestion | 2026-06-30 | 2026-06-30 | embed_image via base64 data URI. chunk_image=1 chunk, empty content. |
| 5 | Hash Change Detection + Scheduler | DONE | 3a | worker-scheduler | 2026-06-30 | 2026-06-30 | All 4 scanner tests pass. Scheduler non-blocking via asyncio.to_thread. |
| 6 | BM25 + Hybrid Retrieval | DONE | 3a | worker-retrieval | 2026-06-30 | 2026-06-30 | BM25 excludes images, RRF fusion verified, rebuild_bm25() ready. |
| 7 | LangGraph RAG Pipeline | DONE | 3b | worker-rag-pipeline | 2026-06-30 | 2026-06-30 | All 5 graph tests pass. app.state.graph set in lifespan. BM25 rebuild wired. |
| 8 | POST /chat Endpoint | DONE | 4 | worker-chat-endpoint | 2026-06-30 | 2026-06-30 | Schema+session isolation verified. TestClient needs context manager. |
| 9 | CLI Client | DONE | 5 | worker-cli | 2026-06-30 | 2026-06-30 | /quit exits 0, unreachable error readable, UUID4 session verified. |

---

## Integration

| Phase | Status | Worker | Notes |
|-------|--------|--------|-------|
| Integration + Full Test Suite | DONE | worker-integration | 56 passed, 0 failed, 0 skipped — 2026-06-30 |

---

## Build Status

**Current Round:** 6 — Integration (COMPLETE)
**Overall:** SHIPPED ✓ — 2026-06-30

---

## Worker Report Log

_(Updated as each worker completes)_

- Round 1 / Issue 1 / worker-scaffold: DONE 2026-06-30. Health endpoint verified. pip bootstrapped --user; future workers use `python3 -m pytest`.
- Round 2 / Issue 2 / worker-ingestion-core: DONE 2026-06-30. All 5 AC verified live with real OpenRouter key. `encoding_format="float"` fix needed for openai SDK v2.44.0 + OpenRouter. Embedding dim = 2048.
- Round 3a / Issue 3 / worker-markdown-ingestion: DONE 2026-06-30. 3 chunks per 3-section doc, file_type="markdown" confirmed.
- Round 3a / Issue 5 / worker-scheduler: DONE 2026-06-30. scan_folder 4/4 tests pass. Excludes hash_store.json from self-tracking.
- Round 3a / Issue 6 / worker-retrieval: DONE 2026-06-30. BM25 excludes images, RRF fusion verified.
- Round 3b / Issue 4 / worker-image-ingestion: DONE 2026-06-30. Pillow validation + raw bytes. embed_image via base64 data URI to VL model.
- Round 3b / Issue 7 / worker-rag-pipeline: DONE 2026-06-30. All 5 graph tests pass. build_graph() factory. app.state.graph in lifespan.
- Round 4 / Issue 8 / worker-chat-endpoint: DONE 2026-06-30. Schema + session isolation verified. TestClient must be used as context manager to trigger lifespan.
- Round 5 / Issue 9 / worker-cli: DONE 2026-06-30. /quit exits 0, unreachable error readable, UUID4 session verified.
- Round 6 / Integration / worker-integration: DONE 2026-06-30. 56 passed, 0 failed, 0 skipped. Fixes applied: conftest import paths corrected to backend.tests.conftest, load_dotenv() added at conftest module level, embed_image() input format fixed (plain string not dict), model updated from claude-3-5-haiku-20241022 to claude-haiku-4-5 in server.py.
