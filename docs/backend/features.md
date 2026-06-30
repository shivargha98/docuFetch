# Features

_Generated from: docs/backend/prd.md_

## Ingestion

### Feature: File Change Detection

Walks the watched folder on each scheduler run, computes a SHA256 hash per file, and compares against the persisted `hash_store.json` to identify new, modified, and deleted files. This is the entry point for all ingestion logic.

**Acceptance criteria:**
- [ ] A new file (hash not in store) is classified as `new` and its path is returned for ingestion.
- [ ] A file whose hash has changed is classified as `modified` and its path is returned for re-ingestion.
- [ ] A file present in the store but absent from disk is classified as `deleted` and its ID is returned for removal.
- [ ] `hash_store.json` is updated to reflect the current state after each run.
- [ ] Files with unchanged hashes produce no ingestion action.

---

### Feature: Per-File-Type Document Loaders

Loads raw content from each supported file type — PDF via `pdfplumber`, Markdown and TXT via standard file read, and images via Pillow — and returns content in a form the chunkers can consume.

**Acceptance criteria:**
- [ ] A PDF file is loaded and returns a non-empty string of extracted text.
- [ ] A `.md` file is loaded and returns its raw text content, preserving heading markers.
- [ ] A `.txt` file is loaded and returns its raw text content.
- [ ] A JPEG, JPG, or PNG file is loaded and returns raw image bytes.
- [ ] An unsupported file extension raises a clear error rather than silently returning empty content.

---

### Feature: Structure-Aware Chunkers

Splits loaded content into chunks using a strategy that respects the structure of each file type: heading-aware splitting for Markdown, fixed-size with overlap for PDF and TXT, and a single atomic chunk per image.

**Acceptance criteria:**
- [ ] Markdown chunks are split at `#`, `##`, and `###` headers; no chunk spans two sections.
- [ ] PDF and TXT chunks are at most 512 characters with a 64-character overlap between consecutive chunks.
- [ ] Each image file produces exactly one chunk.
- [ ] Every chunk carries metadata: `filename`, `file_type`, and `file_path` (for images) at minimum.

---

## Embeddings

### Feature: OpenRouter Embedding Client

Sends text strings or raw image bytes to the `nvidia/llama-nemotron-embed-vl-1b-v2:free` model via the OpenRouter API and returns embedding vectors. This is the sole embedding provider for all content types.

**Acceptance criteria:**
- [ ] A text string input returns an embedding vector of consistent dimensionality.
- [ ] A raw image bytes input returns an embedding vector of the same dimensionality as text embeddings.
- [ ] An API error (e.g. invalid key, rate limit) raises an informative exception rather than returning a silent empty result.

---

### Feature: ChromaDB Store Operations

Provides insert, delete, and vector-query operations against the local ChromaDB collection. Text chunks store content and metadata; image chunks store file path in metadata instead of content.

**Acceptance criteria:**
- [ ] Inserting a text chunk stores its content and metadata (`filename`, `file_type`) and the chunk is retrievable by vector query.
- [ ] Inserting an image chunk stores its `file_path` in metadata (no content field) and the chunk is retrievable by vector query.
- [ ] Deleting by filename removes all chunks associated with that filename from the collection.
- [ ] A vector query for top-K returns at most K results with their metadata intact.

---

## Retrieval

### Feature: BM25 Index

Builds an in-memory BM25 index from all text chunks stored in ChromaDB at startup. Supports keyword-based retrieval returning ranked text chunk candidates. Images are excluded from this index.

**Acceptance criteria:**
- [ ] The BM25 index is populated from all stored text chunks at startup.
- [ ] A keyword query returns ranked text chunks ordered by BM25 score.
- [ ] Image chunks are absent from BM25 results regardless of query terms.
- [ ] The index can be rebuilt from scratch without restarting the server (for use after re-ingestion).

---

### Feature: Hybrid Retriever with RRF Fusion

Runs BM25 and ChromaDB vector similarity retrieval in parallel via `EnsembleRetriever`, fuses the two ranked lists using Reciprocal Rank Fusion (`1 / (rank + 60)`), and returns the top-3 final chunks.

**Acceptance criteria:**
- [ ] For a given query, both BM25 and vector retrievers each return up to 5 candidates.
- [ ] The fused result set contains at most 3 chunks after RRF re-ranking and deduplication.
- [ ] A chunk that ranks highly in both retrievers scores higher in the fused list than one that ranks highly in only one.
- [ ] The final result includes both text and image chunks (images participate in vector search only).

---

## Graph

### Feature: LangGraph State Schema

Defines `DocuFetchState` as the shared TypedDict that flows through every node in the LangGraph pipeline, carrying conversation history, the current query, retrieved chunks, relevance verdict, and source filenames.

**Acceptance criteria:**
- [ ] `DocuFetchState` contains fields: `messages` (list), `query` (str), `retrieved_chunks` (list), `is_relevant` (bool), `sources` (list[str]).
- [ ] The state can be instantiated with any subset of fields defaulted without error.
- [ ] Passing the state through a node returns an updated state with only the modified fields changed.

---

### Feature: Retrieve Node

Executes hybrid retrieval using the current `query` from state and writes the top-3 chunks into `retrieved_chunks`. This node is the first step in the LangGraph pipeline for every query.

**Acceptance criteria:**
- [ ] Given a non-empty `query`, `retrieved_chunks` is populated with 1–3 chunk objects.
- [ ] Each chunk in `retrieved_chunks` carries a `filename` in its metadata.
- [ ] An empty ChromaDB (no documents ingested) results in `retrieved_chunks` being an empty list, not an error.

---

### Feature: Relevance Check Node

Calls Claude Haiku with the current query and retrieved chunks to judge whether the chunks are relevant. Sets `is_relevant` to `True` or `False` on the state. This verdict drives the conditional routing edge.

**Acceptance criteria:**
- [ ] When chunks are clearly relevant to the query, `is_relevant` is set to `True`.
- [ ] When chunks are clearly unrelated to the query, `is_relevant` is set to `False`.
- [ ] When `retrieved_chunks` is empty, `is_relevant` is set to `False` without making an LLM call.

---

### Feature: Generate Node

Calls Claude Haiku to produce a 2–4 sentence answer grounded in `retrieved_chunks`, populates `sources` with the unique filenames from those chunks, and appends the answer as an `AIMessage` to `messages`.

**Acceptance criteria:**
- [ ] The returned answer is between 2 and 4 sentences in length.
- [ ] The `sources` list contains the filenames of all chunks used in the answer, with no duplicates.
- [ ] The answer references source filenames inline (e.g. `[source: policy.pdf]`).
- [ ] The answer is appended to the `messages` history as an `AIMessage`.

---

### Feature: No-Results Node

Returns the standard "no relevant information" response when the relevance check node determines that retrieved chunks do not answer the query. Appends this message to history so multi-turn context is preserved.

**Acceptance criteria:**
- [ ] The node returns exactly: `"I couldn't find relevant information in your documents."`
- [ ] `sources` is an empty list in the returned state.
- [ ] The no-results message is appended to `messages` as an `AIMessage`.

---

### Feature: LangGraph Graph Assembly

Wires the four nodes (`retrieve`, `relevance_check`, `generate`, `no_results`) into a compiled LangGraph graph with a conditional edge that routes from `relevance_check` to either `generate` or `no_results` based on `is_relevant`.

**Acceptance criteria:**
- [ ] Invoking the graph with a relevant query routes through `generate` and returns an answer with sources.
- [ ] Invoking the graph with an irrelevant query routes through `no_results` and returns the standard no-results message.
- [ ] The `messages` history in state accumulates across multiple graph invocations within the same session.
- [ ] History is trimmed to the last 20 messages before each LLM call.

---

## API

### Feature: POST /chat Endpoint

Accepts a query and session ID, invokes the LangGraph pipeline with the session's conversation history, and returns the answer, source filenames, and session ID. Manages per-session message history on `app.state.sessions`.

**Acceptance criteria:**
- [ ] A `POST /chat` with a valid `query` and `session_id` returns `{ "answer": "...", "sources": [...], "session_id": "..." }`.
- [ ] Sending two queries with the same `session_id` produces a response that is aware of the first query's context.
- [ ] Sending a query with a new `session_id` starts a fresh conversation with no history.
- [ ] History is capped at 20 messages; older messages are dropped before the LLM call.

---

### Feature: GET /health Endpoint

Returns the server's running status and a flag indicating whether the initial ingestion run (triggered at startup) has completed.

**Acceptance criteria:**
- [ ] `GET /health` returns HTTP 200 with `{ "status": "ok", "initial_ingestion_complete": <bool> }`.
- [ ] `initial_ingestion_complete` is `false` before the startup ingestion run finishes.
- [ ] `initial_ingestion_complete` is `true` after the startup ingestion run completes.

---

### Feature: POST /ingest Endpoint

Allows a client to manually trigger an immediate ingestion run outside of the 60-second scheduler cycle. Returns a confirmation that the run was triggered.

**Acceptance criteria:**
- [ ] `POST /ingest` returns HTTP 200 with a confirmation message.
- [ ] The ingestion run executes synchronously or is scheduled to run immediately (not deferred to the next 60s tick).
- [ ] After the call, newly added files in the watched folder are indexed and queryable.

---

### Feature: GET /ingest/status Endpoint

Returns the number of currently ingested documents, the timestamp of the last ingestion run, and any error from the last run.

**Acceptance criteria:**
- [ ] `GET /ingest/status` returns `{ "doc_count": <int>, "last_run_at": <timestamp|null>, "last_error": <string|null> }`.
- [ ] `doc_count` reflects the current number of documents (not chunks) in ChromaDB.
- [ ] `last_run_at` is `null` before the first ingestion run.
- [ ] `last_error` is `null` when the last run completed without errors.

---

### Feature: Startup Scheduler

Launches an asyncio background task via FastAPI's `lifespan` context manager that runs ingestion once immediately at startup, then loops with a 60-second sleep between runs.

**Acceptance criteria:**
- [ ] Ingestion begins automatically when the server starts, before the first request is served.
- [ ] After the startup run, ingestion runs again approximately every 60 seconds without manual intervention.
- [ ] The scheduler does not block the FastAPI event loop (queries can be served during ingestion).
- [ ] The scheduler shuts down cleanly when the server stops.

---

## CLI

### Feature: Interactive CLI Client

A standalone `cli.py` script that uses `httpx` to call the running FastAPI server. Generates a UUID4 session ID on startup, sends user queries to `POST /chat`, and supports `/ingest`, `/status`, and `/quit` commands.

**Acceptance criteria:**
- [ ] Running `cli.py` presents a prompt and sends typed input to `POST /chat`, printing the answer and source filenames.
- [ ] `/ingest` calls `POST /ingest` and prints the confirmation message.
- [ ] `/status` calls `GET /ingest/status` and prints doc count, last run time, and any error.
- [ ] `/quit` exits the CLI cleanly.
- [ ] The same `session_id` is reused for all queries within a single CLI session, enabling multi-turn conversation.
- [ ] If the server is not reachable, the CLI prints a clear error rather than crashing with a traceback.
