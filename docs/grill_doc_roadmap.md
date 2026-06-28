# DocuFetch — Grill Session Roadmap

All architectural decisions for the backend, resolved in order of dependency.

---

## The App in One Paragraph

DocuFetch is a personal RAG backend. It watches a single folder (path from `.env`), ingests documents (PDF, Markdown, TXT, JPEG, JPG, PNG), creates embeddings via OpenRouter's `nvidia/llama-nemotron-embed-vl-1b-v2:free`, and stores them in a local ChromaDB. When a user asks a question via the CLI, the system runs hybrid retrieval (BM25 + vector similarity, fused via RRF), checks retrieved chunks for relevance using Claude Haiku, then generates a 2–4 sentence answer with source filename citations. Multi-turn chat history is maintained per CLI session.

---

## Decision Log

### Q1 — Image handling with the VL embedding model
**Decision: Direct vision embedding (Option A)**

Raw image bytes are sent to the VL embedding model. No OCR. The model's visual capability is used directly. This preserves visual information that OCR would discard.

---

### Q2 — What ChromaDB stores for image chunks
**Decision: Store image file path in metadata (Option A1)**

At ingest time, ChromaDB stores the image file path in chunk metadata (not the image bytes, not a caption). At query time, the image is reloaded from disk and sent to Claude Haiku as a vision input. This keeps ingestion cheap (no extra LLM call) and is safe since the watched folder is fixed and files aren't expected to move.

---

### Q3 — Chunking strategy for text documents
**Decision: Structure-aware chunking (Option B)**

| File type | Splitter | Parameters |
|-----------|----------|------------|
| Markdown | `MarkdownHeaderTextSplitter` | Split on `#`, `##`, `###` headers |
| PDF | `RecursiveCharacterTextSplitter` | 512 chars, 64 char overlap |
| TXT | `RecursiveCharacterTextSplitter` | 512 chars, 64 char overlap |
| JPEG/JPG/PNG | No text chunking — one chunk per image | — |

Markdown's header structure is a valuable semantic signal. PDFs and TXT use fixed-size splitting. Images are treated as atomic single chunks.

---

### Q4 — Hybrid retrieval fusion strategy
**Decision: Reciprocal Rank Fusion via `EnsembleRetriever` (Option A)**

Two retrievers run in parallel:
- **BM25** (`rank_bm25`, in-memory, rebuilt from stored text chunks at startup)
- **Vector similarity** (ChromaDB cosine similarity)

Results are fused using RRF: each chunk is scored as `1 / (rank + 60)` from each retriever; scores are summed and re-ranked. LangChain's `EnsembleRetriever` implements this out of the box.

**Images are silently excluded from the BM25 retriever** (no text to keyword-match). They participate only in vector similarity retrieval.

---

### Q5 — Incremental ingestion / change detection
**Decision: Hash-based tracking with a JSON state file (Option A)**

At each scheduler run:
1. Compute SHA256 hash of every file in the watched folder.
2. Compare against hashes stored in `hash_store.json`.
3. **New file** (hash not in store): ingest and add to ChromaDB.
4. **Modified file** (hash changed): delete old ChromaDB chunks for that file, re-ingest.
5. **Deleted file** (in store but not on disk): delete its ChromaDB chunks, remove from store.

The `hash_store.json` file lives alongside the ChromaDB data directory (path configurable via `.env`).

---

### Q6 — Scheduler type and interval
**Decision: asyncio background task, 60-second polling interval (Option B)**

An `asyncio` background task launched via FastAPI's `lifespan` context manager. A `while True: await asyncio.sleep(60)` loop. Zero extra dependencies, adequate for a single periodic job. APScheduler is unnecessary overhead for one job.

Ingestion also runs **once immediately at startup** before the scheduler loop begins, so the vector store is populated before the first query arrives.

---

### Q7 — LangChain LCEL chain vs LangGraph
**Decision: LangGraph from the start (Option B)**

The RAG pipeline is implemented as a LangGraph graph, not a simple LCEL chain. This enables conditional routing (e.g. relevance check node), is extensible for future agent-style workflows, and the added complexity is justified by the routing requirement from Q9.

---

### Q8 — Single-turn vs multi-turn chat
**Decision: Multi-turn with in-memory history per CLI session (Option B)**

LangGraph state includes a `messages` list (`HumanMessage` + `AIMessage` history). Each new query is answered in context of prior exchanges. Conversation history is stored in an in-memory `dict` on `app.state.sessions`, keyed by `session_id`. History is capped at the **last 20 messages** to prevent unbounded memory growth. History is lost on server restart.

---

### Q9 — "No relevant document" detection
**Decision: LLM-judged relevance check node (Option C)**

After retrieval, a dedicated LangGraph node calls Claude Haiku to judge: *"Are these chunks relevant to the question? Answer yes or no."* A conditional edge then routes:
- **Relevant** → `generate` node (produce the answer)
- **Not relevant** → `no_results` node (return: *"I couldn't find relevant information in your documents."*)

This avoids threshold tuning entirely and is more robust than score-based cutoffs.

---

### Q10 — LLM API for Claude Haiku
**Decision: Anthropic SDK directly (Option A)**

LangChain's `ChatAnthropic` is used for Claude Haiku calls. First-class vision support (required for image chunks at query time) and official SDK reliability. `ANTHROPIC_API_KEY` is already in `.env`.

OpenRouter is used only for the embedding model.

---

### Q11 — FastAPI endpoints
**Decision: Four endpoints**

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/chat` | Submit a query; returns answer + sources |
| `GET` | `/health` | App status + whether initial ingestion has completed |
| `POST` | `/ingest` | Manually trigger an ingestion run immediately |
| `GET` | `/ingest/status` | Number of ingested docs, last run time, any errors |

**`POST /chat` request:**
```json
{ "query": "What is the refund policy?", "session_id": "uuid-here" }
```

**`POST /chat` response:**
```json
{ "answer": "...", "sources": ["policy.pdf"], "session_id": "uuid-here" }
```

---

### Q12 — CLI design
**Decision: HTTP client CLI calling the running FastAPI server (Option A)**

A separate `cli.py` script uses `httpx` to call the FastAPI endpoints. The FastAPI server must be running first. The CLI generates a UUID session ID on startup and reuses it for the entire session.

**CLI interaction model:**
```
> What is the refund policy?
Answer: ...  [source: policy.pdf]

> /ingest        ← force re-ingestion now
> /status        ← show ingestion status
> /quit
```

---

### Q13 — Retrieval top-k
**Decision: N=5 per retriever, K=3 final**

- BM25 retrieves top-5 candidates
- Vector similarity retrieves top-5 candidates
- RRF fuses the two lists (up to 10 candidates, with deduplication)
- Final top-3 chunks are passed to Claude Haiku

---

### Q14 — Session management
**Decision: Client-generated UUID, in-memory dict, capped at 20 messages (Option A)**

- The CLI generates a `uuid4` on startup and includes it in every `/chat` request.
- The FastAPI server stores `{session_id: [messages]}` in `app.state.sessions` (plain Python dict).
- History is trimmed to the last 20 messages before each LLM call.
- No `POST /session` endpoint needed.

---

### Q15 — Source citation format
**Decision: Filename only (Option A)**

Answers cite only the source filename, e.g. `[source: policy.pdf]`. No page numbers, section headers, or chunk indices. Simple and uniform across all file types.

---

## Architecture Summary

### Phases

**P1 — Ingestion**
- File scanner: walk watched folder, detect new/changed/deleted via SHA256 hash store
- Loaders: `pdfplumber` (PDF), standard file read (TXT/Markdown), Pillow (images)
- Chunkers: `MarkdownHeaderTextSplitter` for `.md`, `RecursiveCharacterTextSplitter` (512 chars, 64 overlap) for PDF/TXT, single chunk per image
- Metadata stored per chunk: `filename`, `file_type`, `file_path` (images only)

**P2 — Embedding Store**
- Embedding model: `nvidia/llama-nemotron-embed-vl-1b-v2:free` via OpenRouter
- Vector store: ChromaDB (local persistence, path from `.env`)
- BM25 index: in-memory, rebuilt from text chunks on each startup
- Scheduler: asyncio background task, 60s interval, runs once immediately at startup

**P3 — Chat / Summarisation**
- Framework: LangGraph
- LLM: Claude Haiku via `ChatAnthropic`
- Retrieval: `EnsembleRetriever` (BM25 + ChromaDB), top-5 each → RRF → top-3
- LangGraph nodes:
  1. `retrieve` — runs hybrid retrieval
  2. `relevance_check` — Claude Haiku judges if chunks are relevant (yes/no)
  3. `generate` — Claude Haiku produces 2–4 sentence answer with filename citations
  4. `no_results` — returns "I couldn't find relevant information" message
- Conditional edge: `relevance_check` → `generate` or `no_results`
- Session state: in-memory dict, UUID-keyed, capped at 20 messages

### LangGraph State Schema
```python
class DocuFetchState(TypedDict):
    messages: list          # HumanMessage + AIMessage history (capped at 20)
    query: str              # current user query
    retrieved_chunks: list  # top-3 chunks from hybrid retrieval
    is_relevant: bool       # result of relevance check
    sources: list[str]      # list of source filenames
```

### Key `.env` Variables
```
WATCH_FOLDER=...
OPENROUTER_API_KEY=...
ANTHROPIC_API_KEY=...
CHROMA_DB_PATH=./chroma_db
HASH_STORE_PATH=./hash_store.json
```

### File Structure (Backend)
```
docuFetch/
├── backend/
│   ├── ingestion/
│   │   ├── scanner.py       # folder walker, hash-based change detection
│   │   ├── loaders.py       # per-file-type loading (PDF, MD, TXT, image)
│   │   └── chunkers.py      # structure-aware chunking logic
│   ├── embeddings/
│   │   ├── embedder.py      # OpenRouter embedding calls
│   │   └── store.py         # ChromaDB read/write operations
│   ├── retrieval/
│   │   ├── bm25.py          # BM25 index build + retrieval
│   │   └── hybrid.py        # EnsembleRetriever + RRF fusion
│   ├── graph/
│   │   ├── state.py         # DocuFetchState TypedDict
│   │   ├── nodes.py         # retrieve, relevance_check, generate, no_results
│   │   └── graph.py         # LangGraph graph assembly
│   └── api/
│       ├── server.py        # FastAPI app, lifespan, scheduler
│       └── routes.py        # /chat, /health, /ingest, /ingest/status
├── cli.py                   # HTTP client CLI (httpx)
├── requirements.txt
└── .env
```
