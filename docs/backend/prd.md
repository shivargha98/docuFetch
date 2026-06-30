# DocuFetch Backend — Product Requirements Document

## Problem Statement

A developer or researcher accumulates a personal collection of documents (PDFs, Markdown notes, plain text files, and images) across one or more folders. Finding specific information inside those documents requires manually opening files and searching — a slow, context-switching-heavy process. There is no way to ask a natural language question and get a concise, cited answer drawn from the actual contents of those files.

## Solution

DocuFetch is a local RAG (Retrieval-Augmented Generation) backend that watches a designated folder, automatically ingests and embeds every supported file, and answers natural language queries by retrieving the most relevant document chunks and generating a concise answer with source citations. The system runs entirely locally (except for API calls to OpenRouter and Anthropic), requires no manual indexing step, and supports multi-turn conversation within a session.

## User Stories

1. As a user, I want the system to automatically detect and ingest new documents placed in my watched folder, so that I do not have to manually trigger indexing every time I add a file.
2. As a user, I want the system to detect when an existing document has changed and re-ingest only that file, so that my answers always reflect the latest version of my documents.
3. As a user, I want the system to detect when a document has been deleted and remove its chunks from the index, so that deleted content no longer appears in answers.
4. As a user, I want PDF documents to be ingested and made searchable, so that my research papers and reports are part of my knowledge base.
5. As a user, I want Markdown files to be ingested with awareness of their heading structure, so that chunks respect section boundaries rather than cutting through them arbitrarily.
6. As a user, I want plain text files to be ingested and chunked into searchable pieces, so that my notes and logs are included in my knowledge base.
7. As a user, I want images (JPEG, JPG, PNG) to be embedded using a vision model so that visual information in diagrams and scanned documents is retrievable.
8. As a user, I want to ask a natural language question via the CLI and receive a 2–4 sentence answer, so that I can get concise information without reading entire documents.
9. As a user, I want answers to cite the source filename, so that I can locate and verify the original document.
10. As a user, I want the system to explicitly tell me when no relevant document was found, so that I know the absence of an answer is meaningful and not a system failure.
11. As a user, I want retrieval to use both keyword and semantic search, so that queries that are phrased differently from the document text still return relevant results.
12. As a user, I want the system to judge whether retrieved chunks are actually relevant before generating an answer, so that I do not receive hallucinated answers sourced from loosely related content.
13. As a user, I want multi-turn conversation within a session, so that I can ask follow-up questions without repeating context from earlier in the conversation.
14. As a user, I want to manually trigger a re-ingestion from the CLI without restarting the server, so that I can force an immediate index refresh when I know I have added new files.
15. As a user, I want to check the ingestion status (number of documents indexed, last run time, any errors) from the CLI, so that I can confirm the system has processed my documents correctly.
16. As a user, I want a health endpoint so that I can confirm the server is running and that the initial ingestion has completed before querying.
17. As a user, I want the system to begin ingesting my folder as soon as the server starts, so that the index is ready before my first query without me doing anything.
18. As a user, I want the system to automatically re-check my folder every 60 seconds, so that recently added documents become searchable with minimal delay.
19. As a user, I want session history to be isolated per CLI session, so that conversations from one terminal window do not bleed into another.
20. As a user, I want the CLI to accept a `/quit` command, so that I can exit cleanly without killing the terminal.
21. As a user, I want source citations formatted as filename only (e.g. `[source: policy.pdf]`), so that citations are readable without being verbose.

## Implementation Decisions

### Modules
- **ingestion/** — file scanning, change detection, loading, and chunking
- **embeddings/** — OpenRouter embedding calls and ChromaDB read/write
- **retrieval/** — BM25 index and hybrid EnsembleRetriever
- **graph/** — LangGraph state, nodes, and graph assembly
- **api/** — FastAPI server, lifespan, scheduler, and route handlers
- **cli.py** — standalone HTTP client CLI

### Ingestion Pipeline
- File scanner walks the watched folder on every scheduler run
- Change detection uses SHA256 hashes stored in `hash_store.json`
- New file: embed and insert into ChromaDB
- Modified file: delete existing ChromaDB chunks for that file, re-embed and re-insert
- Deleted file: delete ChromaDB chunks, remove from hash store
- Supported types: PDF, Markdown (.md), plain text (.txt), JPEG, JPG, PNG

### Chunking Strategy
| File type | Method | Parameters |
|-----------|--------|------------|
| Markdown | MarkdownHeaderTextSplitter | Split on `#`, `##`, `###` headers |
| PDF | RecursiveCharacterTextSplitter | 512 chars, 64 char overlap |
| TXT | RecursiveCharacterTextSplitter | 512 chars, 64 char overlap |
| Images | No chunking — one chunk per image | — |

### Embedding
- Model: `nvidia/llama-nemotron-embed-vl-1b-v2:free` via OpenRouter
- Images are embedded directly (raw bytes to the VL model — no OCR, no captioning)
- Text chunks are embedded as strings

### ChromaDB Storage
- Text chunks store: content, filename, file_type metadata
- Image chunks store: file_path in metadata (image reloaded from disk at query time)
- Local persistence; path set via `CHROMA_DB_PATH` env variable

### Retrieval
- BM25 index rebuilt in-memory from all stored text chunks at startup
- Images are excluded from BM25 (no text to match); they participate in vector search only
- EnsembleRetriever runs BM25 and ChromaDB vector search in parallel
- RRF fusion: score = `1 / (rank + 60)`, summed across retrievers, then re-ranked
- N=5 per retriever, K=3 final chunks passed to the LLM

### LangGraph Pipeline
LangGraph graph with four nodes and one conditional edge:

```
retrieve → relevance_check → [generate | no_results]
```

- `retrieve`: runs hybrid retrieval, populates `retrieved_chunks`
- `relevance_check`: Claude Haiku judges "yes/no" relevance; sets `is_relevant`
- `generate`: Claude Haiku produces a 2–4 sentence answer with filename citations
- `no_results`: returns "I couldn't find relevant information in your documents."

State schema (from prototype):
```python
class DocuFetchState(TypedDict):
    messages: list          # HumanMessage + AIMessage history (capped at 20)
    query: str
    retrieved_chunks: list
    is_relevant: bool
    sources: list[str]
```

### Session Management
- Client-generated UUID4 session ID, included in every `/chat` request body
- Server stores `{session_id: [messages]}` in `app.state.sessions` (plain dict)
- History trimmed to last 20 messages before each LLM call
- History is lost on server restart (acceptable for personal use)

### FastAPI Endpoints
| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/chat` | Submit query; returns answer + sources + session_id |
| `GET` | `/health` | Server status + initial ingestion complete flag |
| `POST` | `/ingest` | Manually trigger immediate ingestion run |
| `GET` | `/ingest/status` | Doc count, last run time, last error |

`POST /chat` request body: `{ "query": "...", "session_id": "uuid" }`
`POST /chat` response body: `{ "answer": "...", "sources": ["file.pdf"], "session_id": "uuid" }`

### Scheduler
- asyncio background task launched via FastAPI `lifespan` context manager
- Runs ingestion once immediately at startup, then loops with `asyncio.sleep(60)`
- No external scheduler dependency (APScheduler not used)

### LLM
- Claude Haiku via LangChain `ChatAnthropic`
- `ANTHROPIC_API_KEY` from `.env`
- Used for both relevance check and answer generation

### CLI
- `cli.py` — standalone script using `httpx`
- Generates UUID4 on startup, reuses for entire session
- Commands: `/ingest`, `/status`, `/quit`
- Requires FastAPI server to be running

### Configuration
All runtime configuration via `.env`:
```
WATCH_FOLDER=...
OPENROUTER_API_KEY=...
ANTHROPIC_API_KEY=...
CHROMA_DB_PATH=./chroma_db
HASH_STORE_PATH=./hash_store.json
```

## Testing Decisions

- **Good tests test external behavior, not implementation details.** A good test calls a public function or HTTP endpoint with specific inputs and asserts on its outputs — it does not assert on which internal functions were called or in which order.
- **Modules to test:**
  - Ingestion: scanner change detection logic, chunker output shape and content per file type
  - Embeddings: ChromaDB store insert/delete/query operations
  - Retrieval: BM25 index build and query, hybrid retrieval output structure
  - Graph nodes: each LangGraph node in isolation, and the full graph end-to-end
  - API routes: all four endpoints via FastAPI's `TestClient`
- **Test types:** unit tests for pure functions (chunkers, hash logic), integration tests for ChromaDB store operations and LangGraph graph execution, and API-level tests using `TestClient`.
- **No mocking of ChromaDB or LangGraph internals** — test against real (in-memory or temp-dir-backed) instances wherever possible to catch integration failures early.

## Out of Scope

- Frontend / web chat UI (planned for a later phase)
- Authentication or multi-user support
- Persistent session history across server restarts
- Document preview or full-text display in responses
- Support for file types beyond PDF, Markdown, TXT, JPEG, JPG, PNG
- Page number or section header citations (filename only)
- Distributed or cloud deployment
- Rate limiting or API key rotation

## Further Notes

- The BM25 index is rebuilt entirely in memory at startup. For very large document collections this may add startup latency — acceptable for a personal-use tool.
- Image file paths in ChromaDB metadata assume the watched folder path is stable. Moving the folder will break image retrieval until re-ingestion.
- OpenRouter is used exclusively for the embedding model. All LLM inference goes through the Anthropic SDK directly.
