# Worker Brief — Issue 5: Hash-Based Change Detection and Startup Scheduler

**Working directory:** `/workspace`
**Issue:** Issue 5 (from docs/backend/issues.md)
**Your report goes to:** `docs/backend/agent-reports/worker-scheduler-report.md`

---

## Context

Issue 2 built a pipeline (`run_ingestion`) that re-ingests ALL files on every call. You are adding:
1. SHA256-based change detection (new scanner module) so the pipeline only processes changed files
2. A startup asyncio scheduler that runs ingestion automatically at startup and every 60 seconds

You own three files in this round: `scanner.py` (new), `pipeline.py` (modify), `server.py` (modify), and `routes.py` (one-line update). Do not touch `loaders.py`, `chunkers.py`, `store.py`, `embedder.py`, or any files in `retrieval/` or `graph/` — other workers are working on those concurrently.

---

## pip Environment

```bash
pip install -r /workspace/requirements.txt --user --break-system-packages
```
Use `python3 -m pytest`. PATH includes `/home/claude/.local/bin`.

---

## Existing Interfaces You Build On

**`backend/ingestion/pipeline.py`** (current):
```python
SUPPORTED_EXTENSIONS = {".txt", ".pdf"}

def run_ingestion(watch_folder: str, store: ChromaStore, embedder: EmbeddingClient) -> dict:
    # Walks folder, re-ingests ALL supported files
    # Returns {"doc_count": int, "last_run_at": str, "last_error": None|str}
```

**`backend/api/server.py`** (current lifespan):
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.chroma_store = ChromaStore(path=os.getenv("CHROMA_DB_PATH", "./chroma_db"))
    app.state.embedder = EmbeddingClient(api_key=os.getenv("OPENROUTER_API_KEY", ""))
    app.state.initial_ingestion_complete = False
    app.state.sessions = {}
    yield
```

**`backend/api/routes.py`** (current POST /ingest call):
```python
result = run_ingestion(os.getenv("WATCH_FOLDER"), request.app.state.chroma_store, request.app.state.embedder)
```

---

## Files to Create / Modify

### 1. `backend/ingestion/scanner.py` (NEW)

```python
"""
SHA256-based file change detection for docuFetch.

Scans the watch folder, computes SHA256 hashes for all files, and compares
against a persisted hash_store.json to classify files as new, modified, or
deleted. Updates hash_store.json after each scan.
"""
import hashlib
import json
from pathlib import Path


def _compute_sha256(path: Path) -> str:
    """Compute the SHA256 hash of a file's contents."""
    ...

def scan_folder(watch_folder: str, hash_store_path: str) -> dict:
    """
    Walk watch_folder and classify files relative to hash_store.json.

    Returns:
        {
            "new": [Path, ...],       # files not in hash store
            "modified": [Path, ...],  # files whose hash changed
            "deleted": [str, ...],    # filenames in store but absent from disk
        }

    Side effect: writes updated hashes to hash_store_path.
    """
    ...
```

Implementation:
- `_compute_sha256`: open file in binary mode, compute `hashlib.sha256(data).hexdigest()`
- `scan_folder`:
  1. Load existing hash store: `json.loads(Path(hash_store_path).read_text())` if it exists, else `{}`
  2. Walk `Path(watch_folder).rglob("*")`, filter to `path.is_file()`
  3. For each file: compute hash, compare to stored hash
     - Not in store → `new`
     - In store, hash different → `modified`
     - In store, hash same → skip
  4. Anything in store but not found on disk → `deleted` (just the filename string)
  5. Build new store dict: all current files and their hashes (deleted files removed)
  6. Write new store: `Path(hash_store_path).write_text(json.dumps(new_store, indent=2))`
  7. Return `{"new": [...], "modified": [...], "deleted": [...]}`

Note: store keys are file basenames (e.g., `"report.pdf"`), not full paths.

### 2. `backend/ingestion/pipeline.py` (MODIFY)

Make two targeted changes:

**Change A — add `hash_store_path` parameter and use scanner:**

Update `run_ingestion` signature:
```python
def run_ingestion(watch_folder: str, store: ChromaStore, embedder: EmbeddingClient, hash_store_path: str) -> dict:
```

Replace the "walk all files and re-ingest" logic with scanner-driven logic:
```python
from backend.ingestion.scanner import scan_folder

changes = scan_folder(watch_folder, hash_store_path)

# Handle deletions
for filename in changes["deleted"]:
    store.delete_by_filename(filename)

# Handle new and modified files
for path in changes["new"] + changes["modified"]:
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        continue
    filename = path.name
    file_type = EXTENSION_TO_FILE_TYPE.get(path.suffix.lower(), path.suffix.lower().lstrip("."))
    store.delete_by_filename(filename)  # safe no-op if not present
    text = load_file(path)
    chunks = chunk_file(text, filename, file_type)
    embeddings = embedder.embed_texts([c.page_content for c in chunks])
    store.insert_chunks(chunks, embeddings)
```

**Change B — add `.md` to SUPPORTED_EXTENSIONS and add EXTENSION_TO_FILE_TYPE mapping:**

```python
SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".md"}

EXTENSION_TO_FILE_TYPE = {
    ".txt": "txt",
    ".pdf": "pdf",
    ".md": "markdown",
    # Image extensions added by Issue 4
}
```

Replace the inline `file_type = path.suffix.lower().lstrip(".")` with:
```python
file_type = EXTENSION_TO_FILE_TYPE.get(path.suffix.lower(), path.suffix.lower().lstrip("."))
```

### 3. `backend/api/server.py` (MODIFY — add scheduler to lifespan)

Add an asyncio background scheduler task to the existing lifespan. The scheduler:
1. Runs ingestion once immediately at startup (before `yield`)
2. Loops with `asyncio.sleep(60)` between runs
3. Runs `run_ingestion` in a thread executor (non-blocking, so FastAPI can serve requests during ingestion)
4. Sets `app.state.initial_ingestion_complete = True` after the first run

```python
import asyncio
from backend.ingestion.pipeline import run_ingestion

async def _ingestion_scheduler(app: FastAPI) -> None:
    """
    Background asyncio task that runs ingestion at startup then every 60 seconds.
    Runs run_ingestion in a thread executor to avoid blocking the event loop.
    """
    watch_folder = os.getenv("WATCH_FOLDER", "")
    hash_store_path = os.getenv("HASH_STORE_PATH", "./hash_store.json")

    # First run at startup
    result = await asyncio.to_thread(
        run_ingestion, watch_folder, app.state.chroma_store, app.state.embedder, hash_store_path
    )
    app.state.ingestion_status = result
    app.state.initial_ingestion_complete = True

    # Loop every 60 seconds
    while True:
        await asyncio.sleep(60)
        result = await asyncio.to_thread(
            run_ingestion, watch_folder, app.state.chroma_store, app.state.embedder, hash_store_path
        )
        app.state.ingestion_status = result
```

Update the lifespan to launch this as a background task:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared state
    app.state.chroma_store = ChromaStore(path=os.getenv("CHROMA_DB_PATH", "./chroma_db"))
    app.state.embedder = EmbeddingClient(api_key=os.getenv("OPENROUTER_API_KEY", ""))
    app.state.initial_ingestion_complete = False
    app.state.sessions = {}

    # Start background ingestion scheduler
    task = asyncio.create_task(_ingestion_scheduler(app))
    yield
    # Shutdown: cancel the scheduler task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
```

### 4. `backend/api/routes.py` (MODIFY — one-line change)

Update the `run_ingestion` call in `POST /ingest` to pass `hash_store_path`:
```python
result = run_ingestion(
    os.getenv("WATCH_FOLDER"),
    request.app.state.chroma_store,
    request.app.state.embedder,
    os.getenv("HASH_STORE_PATH", "./hash_store.json"),
)
```

---

## Acceptance Criteria (verify all before reporting done)

- [ ] A new file added to `WATCH_FOLDER` is returned in the `new` list by `scan_folder`
- [ ] A modified file (hash changed) is returned in the `modified` list by `scan_folder`
- [ ] A deleted file (in store but not on disk) is returned in the `deleted` list
- [ ] `scan_folder` updates `hash_store.json` correctly after each call
- [ ] `GET /health` returns `"initial_ingestion_complete": true` after the startup ingestion completes
- [ ] The scheduler does not block the event loop (verify by checking server responds to `/health` while ingestion would be running)

---

## How to Verify (unit test for scanner — no API keys needed)

Write a scratch test:
```python
import tempfile, json
from pathlib import Path
from backend.ingestion.scanner import scan_folder

with tempfile.TemporaryDirectory() as tmpdir:
    # Test 1: new file
    txt = Path(tmpdir) / "test.txt"
    txt.write_text("hello world")
    store_path = str(Path(tmpdir) / "hash_store.json")
    result = scan_folder(tmpdir, store_path)
    assert "test.txt" in [p.name for p in result["new"]], f"Expected new, got: {result}"
    print("Test 1 passed: new file detected")

    # Test 2: unchanged file
    result2 = scan_folder(tmpdir, store_path)
    assert len(result2["new"]) == 0 and len(result2["modified"]) == 0
    print("Test 2 passed: unchanged file produces no action")

    # Test 3: modified file
    txt.write_text("hello world changed")
    result3 = scan_folder(tmpdir, store_path)
    assert "test.txt" in [p.name for p in result3["modified"]], f"Expected modified, got: {result3}"
    print("Test 3 passed: modified file detected")

    # Test 4: deleted file
    txt.unlink()
    result4 = scan_folder(tmpdir, store_path)
    assert "test.txt" in result4["deleted"], f"Expected deleted, got: {result4}"
    print("Test 4 passed: deleted file detected")
    
    print("All scanner tests passed")
```

Run: `cd /workspace && python3 scratch_scanner.py`

For the scheduler/server test: confirm `GET /health` returns `"initial_ingestion_complete": true` after startup (requires OPENROUTER_API_KEY; if unavailable, confirm via code inspection and note in report).

---

## Coding Standards

- Every new function must have a docstring
- Every new file must have a module-level docstring
- Surgical changes to existing files — touch only what's needed

---

## What to Write in Your Report

Write `docs/backend/agent-reports/worker-scheduler-report.md` with:
1. Status: DONE or FAILED
2. Files created/modified
3. Scanner verification output (paste scratch test results)
4. Server/scheduler verification (curl output or code inspection note)
5. Any deviations and why
6. What Issue 9 (CLI) needs to know about `hash_store.json` location and scheduler behavior
