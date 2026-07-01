# Worker Report — Issue 2: TXT and PDF Ingestion Pipeline

### Status
COMPLETE

---

### What I Built

**Files created:**

- `/workspace/backend/ingestion/loaders.py` — 38 lines. `load_txt`, `load_pdf`, `load_file` dispatch, `UnsupportedFileTypeError`.
- `/workspace/backend/ingestion/chunkers.py` — 33 lines. `chunk_text`, `chunk_file` dispatch using `RecursiveCharacterTextSplitter`.
- `/workspace/backend/embeddings/embedder.py` — 33 lines. `EmbeddingClient` wrapping OpenRouter via openai SDK.
- `/workspace/backend/embeddings/store.py` — 62 lines. `ChromaStore` with `insert_chunks`, `delete_by_filename`, `query`, `get_unique_filenames`.
- `/workspace/backend/ingestion/pipeline.py` — 51 lines. `run_ingestion` orchestrator.

**Files modified:**

- `/workspace/backend/api/routes.py` — 29 lines (was 9). Added `POST /ingest` and `GET /ingest/status` handlers.
- `/workspace/backend/api/server.py` — 40 lines (was 30). Replaced module-level state assignments with a `lifespan` context manager that initializes `ChromaStore`, `EmbeddingClient`, `initial_ingestion_complete`, and `sessions`.

---

### Test Results

All acceptance criteria verified via live curl against the running server (real OPENROUTER_API_KEY from `/workspace/.env`):

**Criterion 1: `GET /ingest/status` returns `last_run_at: null` before any ingestion run**
```
curl -s http://localhost:8003/ingest/status
{"doc_count":0,"last_run_at":null,"last_error":null}
```
PASS

**Criterion 2: `POST /ingest` returns HTTP 200 with confirmation message**
```
curl -s -X POST http://localhost:8003/ingest
{"message":"Ingestion complete","doc_count":1}
```
PASS

**Criterion 3: After ingestion, `GET /ingest/status` returns doc_count > 0 with ISO timestamp**
```
curl -s http://localhost:8003/ingest/status
{"doc_count":1,"last_run_at":"2026-06-30T19:48:38.193974+00:00","last_error":null}
```
PASS

**Criterion 4: Calling `POST /ingest` twice on the same file produces no duplicate chunks**
```
# Second run:
curl -s -X POST http://localhost:8003/ingest
{"message":"Ingestion complete","doc_count":1}
# doc_count is still 1 — no duplicates
```
PASS. Verified by confirming `ChromaDB.get()` returns 1 chunk with ID `test.txt_0` after both runs.

**Criterion 5: Chunks carry `filename` and `file_type` in metadata**
```
Sample metadata: [{'filename': 'test.txt', 'file_type': 'txt'}]
```
PASS

---

### What the Orchestrator Should Know

**encoding_format deviation:** The brief specifies `self._client.embeddings.create(model=..., input=texts)` exactly. However, openai SDK v2.44.0 (installed in this environment) sends `encoding_format: "base64"` by default. OpenRouter's Nvidia embedding model returns `{"error": {"message": "Nvidia embeddings do not support base64 encoding_format. Use float instead, or omit encoding_format."}}` when this is sent. I added `encoding_format="float"` to the `embed_texts` call to fix this. The embedding vectors are functionally identical — this is a transport encoding parameter only, not a change to the model or the interface.

**Empty OPENROUTER_API_KEY causes server startup failure:** The openai SDK raises `OpenAIError: Missing credentials` when `api_key=""`. The server will fail to start if `OPENROUTER_API_KEY` is not set. This is a known constraint: the environment must set a valid (or dummy non-empty) API key for the server to start. Issue 5 or a future deployment issue may want to add a startup check or lazy-init guard.

---

### What the Next Worker Needs

**Issue 3 (Markdown Loader) / Issue 4 (Image Loader):**
- Add a new `load_md(path)` function to `backend/ingestion/loaders.py` and wire it into `load_file`'s dispatch on `.md` suffix. Same pattern as `load_txt`.
- Add a new `chunk_md(...)` or reuse `chunk_text` in `backend/ingestion/chunkers.py` and wire it into `chunk_file`'s dispatch for `"md"`.
- For images, add `load_image(path)` returning raw bytes (or a description string), and add `chunk_image(...)` returning Documents with `file_type="image"`.
- `SUPPORTED_EXTENSIONS` in `backend/ingestion/pipeline.py` must be extended to include `.md` and image extensions when those issues land.

**Issue 5 (Scheduler):**
- `run_ingestion(watch_folder: str, store: ChromaStore, embedder: EmbeddingClient) -> dict` is the entry point. It returns `{"doc_count": int, "last_run_at": str, "last_error": str | None}`.
- `app.state.chroma_store` and `app.state.embedder` are initialized in the lifespan and available at `request.app.state`.
- The scheduler should write its result to `app.state.ingestion_status` (same key the POST /ingest route uses) so `GET /ingest/status` reflects scheduled runs too.

**Issue 6 (Hybrid Retriever):**
- `ChromaStore.query(embedding: list[float], top_k: int = 3) -> list[Document]` — returns LangChain `Document` objects with `page_content` and `metadata`.
- `ChromaStore` is at `backend/embeddings/store.py`, collection name is `"docufetch"`.
- Embedding dimension is 2048 (nvidia/llama-nemotron-embed-vl-1b-v2:free via OpenRouter).

**Issue 8 (Chat route):**
- `EmbeddingClient.embed_texts(texts: list[str]) -> list[list[float]]` — call this to embed a query string before calling `ChromaStore.query`.
- `app.state.embedder` is an `EmbeddingClient` instance, available via `request.app.state.embedder`.

---

### Blockers
None.
