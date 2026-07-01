# Worker Brief — Issue 2: TXT and PDF Ingestion Pipeline with Manual Trigger and Status

**Working directory:** `/workspace`
**Issue:** Issue 2 (from docs/backend/issues.md)
**Your report goes to:** `docs/backend/agent-reports/worker-ingestion-core-report.md`

---

## Context

The scaffold from Issue 1 is complete. The FastAPI app is in `backend/api/server.py`, imported by a root `server.py` shim. Routes are registered via a `router = APIRouter()` in `backend/api/routes.py` which `server.py` already includes. All `backend/` package `__init__.py` files exist.

You are building the first complete vertical slice: TXT and PDF files only. You will prove the full path from file on disk → load → chunk → embed → ChromaDB → API response. Issues 3 (Markdown) and 4 (Image) will extend your loaders and chunkers later — design those files for extension but do not build beyond TXT/PDF now.

---

## pip / Python Environment

pip was bootstrapped with `--user --break-system-packages`. Run installs and tests as:
```bash
pip install -r /workspace/requirements.txt --user --break-system-packages
python3 -m pytest
```
PATH should include `/home/claude/.local/bin` for `python3 -m pytest` to work. If not, use `python3 -m pytest` directly.

---

## Files to Create

### 1. `backend/ingestion/loaders.py`

Two public functions. No other logic.

```python
"""
Per-file-type document loaders for docuFetch.

Each loader reads a single file and returns its content in a form the
chunkers can consume. Unsupported extensions raise UnsupportedFileTypeError.
"""
from pathlib import Path

class UnsupportedFileTypeError(Exception):
    """Raised when a file with an unsupported extension is passed to a loader."""
    pass

def load_txt(path: Path) -> str:
    """Load a plain-text file and return its content as a string."""
    ...

def load_pdf(path: Path) -> str:
    """Load a PDF file using pdfplumber and return all extracted text as a single string."""
    ...
```

- `load_txt`: open and read the file, return the string
- `load_pdf`: use `pdfplumber.open(path)`, iterate pages, join all `page.extract_text()` results with `\n`
- **Do not add a loader for markdown or images yet** — those come in Issues 3 and 4. Any call to load a `.md` or `.png` etc. should raise `UnsupportedFileTypeError("Unsupported file type: .md")`.
- Add a dispatch function `load_file(path: Path) -> str` that routes based on suffix:
  - `.txt` → `load_txt`
  - `.pdf` → `load_pdf`
  - anything else → raise `UnsupportedFileTypeError(f"Unsupported file type: {path.suffix}")`

### 2. `backend/ingestion/chunkers.py`

Uses LangChain's `RecursiveCharacterTextSplitter` for TXT/PDF. Returns `langchain_core.documents.Document` objects (because Issue 6's hybrid retriever expects Documents).

```python
"""
Structure-aware document chunkers for docuFetch.

Each chunker takes loaded content and returns a list of LangChain Document
objects with page_content and metadata fields. Image chunking is added in
Issue 4.
"""
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(text: str, filename: str, file_type: str) -> list[Document]:
    """
    Split text into chunks of at most 512 chars with 64-char overlap.
    Each chunk carries filename and file_type in its metadata.
    Used for both TXT and PDF files.
    """
    ...
```

- Use `RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)`
- Each produced `Document` has `page_content=<chunk_text>` and `metadata={"filename": filename, "file_type": file_type}`
- **Do not add markdown or image chunking yet** — those come in Issues 3 and 4.
- Add a dispatch function `chunk_file(text: str, filename: str, file_type: str) -> list[Document]` that delegates to `chunk_text` for "txt" and "pdf" types, and raises `ValueError(f"No chunker for file type: {file_type}")` for unknown types.

### 3. `backend/embeddings/embedder.py`

OpenRouter embedding client using the `openai` SDK pointed at OpenRouter's base URL.

```python
"""
OpenRouter embedding client for docuFetch.

Sends text strings to the nvidia/llama-nemotron-embed-vl-1b-v2:free model
via the OpenRouter API (OpenAI-compatible) and returns embedding vectors.
Image embedding (raw bytes) is added in Issue 4.
"""
import os
import openai

OPENROUTER_EMBED_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2:free"

class EmbeddingClient:
    """Wraps the OpenRouter embedding API."""

    def __init__(self, api_key: str):
        """Initialise the OpenAI-compatible client pointed at OpenRouter."""
        self._client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Embed a list of text strings. Returns one vector per input string.
        Raises openai.OpenAIError on API failure.
        """
        response = self._client.embeddings.create(
            model=OPENROUTER_EMBED_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]
```

Do not add `embed_image` yet — that comes in Issue 4.

### 4. `backend/embeddings/store.py`

ChromaDB operations class. Uses the `chromadb` package directly (not the LangChain wrapper).

```python
"""
ChromaDB vector store operations for docuFetch.

Provides insert, delete, and query operations against the local ChromaDB
collection. Text chunks store content and metadata; image chunks (added in
Issue 4) store file_path in metadata only.
"""
import chromadb
from langchain_core.documents import Document

COLLECTION_NAME = "docufetch"

class ChromaStore:
    """Manages a ChromaDB collection for docuFetch."""

    def __init__(self, path: str):
        """Open (or create) a PersistentClient at path and get/create the collection."""
        self._client = chromadb.PersistentClient(path=path)
        self._collection = self._client.get_or_create_collection(COLLECTION_NAME)

    def insert_chunks(self, chunks: list[Document], embeddings: list[list[float]]) -> None:
        """
        Insert Document chunks with their embeddings into the collection.
        IDs are generated as filename_chunkindex to be deterministic.
        """
        ...

    def delete_by_filename(self, filename: str) -> None:
        """Delete all chunks whose metadata filename matches the given filename."""
        ...

    def query(self, embedding: list[float], top_k: int = 3) -> list[Document]:
        """
        Run a vector similarity query. Returns at most top_k Documents
        with their metadata intact.
        """
        ...

    def get_unique_filenames(self) -> list[str]:
        """Return the list of unique filenames currently stored in the collection."""
        ...
```

Implementation notes:
- `insert_chunks`: generate IDs as `f"{chunk.metadata['filename']}_{i}"` where i is the index. Call `self._collection.add(ids=[...], documents=[c.page_content for c in chunks], embeddings=embeddings, metadatas=[c.metadata for c in chunks])`.
- `delete_by_filename`: use `self._collection.delete(where={"filename": filename})`.
- `query`: use `self._collection.query(query_embeddings=[embedding], n_results=top_k)`. Convert results back to `Document(page_content=doc, metadata=meta)` objects. Handle the case where the collection has fewer than top_k items.
- `get_unique_filenames`: get all metadata via `self._collection.get(include=["metadatas"])`, extract `m["filename"]` for each, return `list(set(...))`.

### 5. `backend/ingestion/pipeline.py`

The pipeline orchestrator. This is called by the POST /ingest route AND will be called by Issue 5's scheduler.

```python
"""
Ingestion pipeline orchestrator for docuFetch.

Walks the watch folder, identifies supported files (.txt, .pdf at this stage),
deletes their existing ChromaDB chunks, reloads, rechunks, re-embeds, and
reinserts. Returns a result dict with doc_count and error.
"""
import os
from datetime import datetime, timezone
from pathlib import Path

from backend.ingestion.loaders import load_file, UnsupportedFileTypeError
from backend.ingestion.chunkers import chunk_file
from backend.embeddings.embedder import EmbeddingClient
from backend.embeddings.store import ChromaStore

SUPPORTED_EXTENSIONS = {".txt", ".pdf"}

def run_ingestion(watch_folder: str, store: ChromaStore, embedder: EmbeddingClient) -> dict:
    """
    Walk watch_folder, ingest all supported files into store using embedder.

    For each file:
    - Delete existing chunks (idempotent upsert: prevents duplicates)
    - Load, chunk, embed, insert

    Returns {"doc_count": int, "last_run_at": str (ISO8601), "last_error": None or str}.
    """
    ...
```

Logic:
1. Walk `watch_folder` with `Path(watch_folder).rglob("*")`, filter to files with `SUPPORTED_EXTENSIONS`
2. For each file: call `store.delete_by_filename(filename)`, then `load_file(path)`, then `chunk_file(text, filename, file_type)`, then `embedder.embed_texts([c.page_content for c in chunks])`, then `store.insert_chunks(chunks, embeddings)`
3. Track how many files were successfully processed
4. After all files, call `store.get_unique_filenames()` to get current doc count
5. Return `{"doc_count": len(store.get_unique_filenames()), "last_run_at": datetime.now(timezone.utc).isoformat(), "last_error": None}` on success, or include the error string on failure

### 6. `backend/api/routes.py` (extend the existing stub)

Add POST /ingest and GET /ingest/status to the existing router. The existing file has only `router = APIRouter()`.

```python
"""
API route handlers for docuFetch.

Exposes: POST /ingest (manual trigger), GET /ingest/status, and stubs for
future routes (/chat added in Issue 8).
"""
import os
from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/ingest")
def ingest(request: Request):
    """Trigger an immediate ingestion run over WATCH_FOLDER."""
    ...

@router.get("/ingest/status")
def ingest_status(request: Request):
    """Return doc_count, last_run_at, and last_error from the last ingestion run."""
    ...
```

- POST /ingest: call `run_ingestion(os.getenv("WATCH_FOLDER"), request.app.state.chroma_store, request.app.state.embedder)`, store result in `request.app.state.ingestion_status`, return `{"message": "Ingestion complete", "doc_count": result["doc_count"]}`
- GET /ingest/status: if `not hasattr(request.app.state, "ingestion_status")`, return `{"doc_count": 0, "last_run_at": None, "last_error": None}`. Otherwise return `request.app.state.ingestion_status`.

### 7. `backend/api/server.py` (minimal addition)

Add ChromaStore and EmbeddingClient initialization. Modify the existing server.py to initialize these on the `app` object **after** the existing code, in a startup lifespan:

```python
from contextlib import asynccontextmanager
import os
from backend.embeddings.store import ChromaStore
from backend.embeddings.embedder import EmbeddingClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared resources at startup."""
    app.state.chroma_store = ChromaStore(path=os.getenv("CHROMA_DB_PATH", "./chroma_db"))
    app.state.embedder = EmbeddingClient(api_key=os.getenv("OPENROUTER_API_KEY", ""))
    yield

app = FastAPI(title="docuFetch", lifespan=lifespan)
```

The existing `app.state.initial_ingestion_complete = False` and `app.state.sessions = {}` assignments should move inside the lifespan's startup block (before `yield`). The lifespan replaces setting these at module level.

Keep the health endpoint unchanged. Keep `app.include_router(router)` unchanged.

---

## Acceptance Criteria (verify all before reporting done)

- [ ] `POST /ingest` returns HTTP 200 with a confirmation message (`{"message": ..., "doc_count": N}`)
- [ ] After ingestion, `GET /ingest/status` returns `{"doc_count": N, "last_run_at": "<timestamp>", "last_error": null}` where N > 0 when a test file exists
- [ ] Calling `POST /ingest` twice on the same file produces no duplicate chunks (verify by checking ChromaDB chunk count stays the same)
- [ ] Chunks in ChromaDB carry `filename` and `file_type` in their metadata
- [ ] `GET /ingest/status` returns `last_run_at: null` before any ingestion run

---

## How to Verify

Create a test .txt file, set WATCH_FOLDER, and call the endpoints:

```bash
export WATCH_FOLDER=/tmp/test_docs
export OPENROUTER_API_KEY=<your key>
export CHROMA_DB_PATH=/tmp/chroma_test
mkdir -p $WATCH_FOLDER
echo "The quick brown fox jumps over the lazy dog. This is a test document for docuFetch ingestion. It contains enough text to be meaningful." > $WATCH_FOLDER/test.txt

cd /workspace
uvicorn server:app --port 8000 &
sleep 3

curl -s http://localhost:8000/ingest/status
# Expected: {"doc_count":0,"last_run_at":null,"last_error":null}

curl -s -X POST http://localhost:8000/ingest
# Expected: {"message":"Ingestion complete","doc_count":1}

curl -s http://localhost:8000/ingest/status
# Expected: {"doc_count":1,"last_run_at":"<ISO timestamp>","last_error":null}

# Call /ingest again — same file, no change
curl -s -X POST http://localhost:8000/ingest
# Expected: doc_count still 1, no duplicates

kill %1
```

If OPENROUTER_API_KEY is not available in the environment, note this in your report and describe what you verified via code inspection instead.

---

## Coding Standards

- Every file must have a module-level docstring at the top
- Every function/method must have a docstring
- Simplicity first — no extra features, no abstractions beyond what's specified here
- Do not add a markdown loader, image loader, or their chunkers — those are Issues 3 and 4

---

## What to Write in Your Report

Write `docs/backend/agent-reports/worker-ingestion-core-report.md` with:
1. Status: DONE or FAILED
2. Every file created or modified
3. Verification output (paste actual curl/test responses, or describe what you confirmed via code inspection if API keys unavailable)
4. Interface decisions made that Issues 3, 4, 5, 6 workers need to know:
   - Exact signatures of `load_file`, `chunk_file`, `run_ingestion`
   - ChromaStore method signatures
   - EmbeddingClient method signatures
   - How `app.state.chroma_store` and `app.state.embedder` are initialized
5. Any deviations from this brief and why
