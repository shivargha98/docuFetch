# Worker Scheduler Report

### Status
COMPLETE

### What I Built

**Files created:**
- `/workspace/backend/ingestion/scanner.py` — 66 lines. New module implementing SHA256-based file change detection (`_compute_sha256`, `scan_folder`). Classifies files as new, modified, or deleted relative to a persisted `hash_store.json`. Excludes the hash store file itself from being tracked (prevents self-referential churn when hash_store.json lives inside the watch folder).

**Files modified:**
- `/workspace/backend/ingestion/pipeline.py` — Changed signature of `run_ingestion` to accept `hash_store_path: str`. Replaced full-rescan loop with `scan_folder`-driven logic (handles deletions, processes only new/modified files). Added `.md` to `SUPPORTED_EXTENSIONS`. Added `EXTENSION_TO_FILE_TYPE` mapping. Removed now-orphaned `Path` import. (~15 lines changed)
- `/workspace/backend/api/server.py` — Added `asyncio` import and `run_ingestion` import. Added `_ingestion_scheduler` async function. Updated `lifespan` to launch scheduler as a background task and cancel it on shutdown. (~30 lines added)
- `/workspace/backend/api/routes.py` — Added `hash_store_path` argument to `run_ingestion` call in `POST /ingest`. (1 line changed)

### Test Results

Scratch test run (`python3 scratch_scanner.py`):

```
Test 1 passed: new file detected
Test 2 passed: unchanged file produces no action
Test 3 passed: modified file detected
Test 4 passed: deleted file detected
All scanner tests passed
```

**Scheduler/server test:** No OPENROUTER_API_KEY available in the environment; live server test skipped. Code inspection confirms non-blocking behavior:
- `_ingestion_scheduler` uses `asyncio.to_thread(run_ingestion, ...)` which offloads the synchronous ingestion to a thread pool worker, freeing the event loop to serve requests (including `/health`) during ingestion.
- `app.state.initial_ingestion_complete` is set to `True` only after the first `run_ingestion` call returns, so `GET /health` will reflect the correct state once the background task completes its first run.
- Scheduler task is cancelled gracefully on shutdown via `task.cancel()` + `CancelledError` suppression.

### What the Orchestrator Should Know

1. **Scanner excludes hash_store.json from tracking.** If `HASH_STORE_PATH` resolves to a file inside `WATCH_FOLDER` (as in the test), the scanner skips that file via `path.resolve() == store_file.resolve()`. This is a one-line guard that prevents infinite churn. Not in the original brief spec, but required by the test.

2. **Basename collision risk.** The hash store uses `path.name` (basename) as the key. Two files in different subdirectories of the watch folder with the same basename will collide — the second one scanned silently overwrites the first in the hash store. The brief specifies basename keys explicitly; this is a known limitation not addressed here.

3. **`UnsupportedFileTypeError` import in pipeline.py was pre-existing dead code** — not removed per coding standards (touch only your own mess).

4. **`HASH_STORE_PATH` default** is `"./hash_store.json"` (CWD of the server process). If the server's CWD changes between restarts, the hash store will be lost and all files will be re-ingested on the next startup.

### What the Next Worker Needs

**Issue 9 (CLI):** `run_ingestion` now requires a 4th positional argument: `hash_store_path: str`. Any CLI invocation must pass this. Recommended value: `os.getenv("HASH_STORE_PATH", "./hash_store.json")`. The hash store is a plain JSON file mapping filenames to SHA256 hex digests — safe to inspect, copy, or delete manually. Deleting it forces full re-ingestion on the next run.

**Scheduler behavior:** At server startup, the background scheduler runs `run_ingestion` once immediately (before `yield` in lifespan) and then every 60 seconds in a loop. The CLI should not need to start its own scheduler — it can call `run_ingestion` directly as a one-shot sync call.

### Blockers
None.
