### Status
COMPLETE

### What I Built

**`backend/ingestion/loaders.py`** — modified (49 lines total, was 49)
- Added `from PIL import Image` import
- Added `load_image(path: Path) -> bytes` function (13 lines): opens + validates with `Image.verify()`, returns raw bytes, raises `UnsupportedFileTypeError` on failure
- Updated `load_file` return type hint from `str` to `str | bytes`
- Added `.jpg`, `.jpeg`, `.png` branch to `load_file` dispatch

**`backend/ingestion/chunkers.py`** — modified (66 lines total, was 52)
- Added `from pathlib import Path` import
- Added `chunk_image(path: Path, filename: str) -> list[Document]` function (11 lines): returns a single Document with empty `page_content` and metadata containing `filename`, `file_type: "image"`, `file_path` (absolute)
- Changed `chunk_file` signature from `(text: str, ...)` to `(content: str | bytes, ..., path: Path = None)`
- Added `image` branch to `chunk_file` dispatch

**`backend/embeddings/embedder.py`** — modified (55 lines total, was 34)
- Added `import base64`
- Added module-level `_MIME_TYPES` dict mapping `.jpg`/`.jpeg`/`.png` to MIME type strings
- Added `embed_image(self, image_bytes: bytes, suffix: str = ".jpg") -> list[float]` method (15 lines): base64-encodes bytes, sends as data URI to OpenRouter VL model, returns single embedding vector

**`backend/ingestion/pipeline.py`** — modified (67 lines total, was 63)
- Updated `SUPPORTED_EXTENSIONS` to include `.jpg`, `.jpeg`, `.png`
- Updated `EXTENSION_TO_FILE_TYPE` with three image extension entries (all map to `"image"`)
- Updated import line to include `load_image` from loaders and `chunk_image` from chunkers
- Replaced single-path ingestion loop body with branching version: `file_type == "image"` takes the `load_image → chunk_image → embed_image → insert_chunks([embedding])` path; all other types keep the existing text path

### Test Results

**Scratch test — `load_image` returns bytes:**
```
Image bytes loaded: 633 bytes   PASS
```

**Scratch test — `chunk_image` produces exactly one chunk:**
```
Image chunk metadata: {'filename': 'test.jpg', 'file_type': 'image', 'file_path': '/tmp/tmpz93xwx9t/test.jpg'}   PASS
```

**Additional verification — `load_file` dispatch for `.jpg`, `.jpeg`, `.png`:**
```
load_file(.jpg): returned bytes (633 bytes)   PASS
load_file(.jpeg): returned bytes (633 bytes)  PASS
load_file(.png): returned bytes (77 bytes)    PASS
```

**Additional verification — `UnsupportedFileTypeError` still fires for unsupported types:** PASS

**Additional verification — `chunk_file` image dispatch:** PASS

**Additional verification — `embed_image` signature `(self, image_bytes: bytes, suffix: str = '.jpg') -> list[float]`:** PASS

**Additional verification — pipeline constants:** PASS

**`embed_image` actual API call:** Not executed — `OPENROUTER_API_KEY` is not available in this environment. The function exists, its signature is correct, and its structure matches the brief exactly (base64 data URI, same model as `embed_texts`, returns `response.data[0].embedding`).

**Pre-existing pytest stubs:** Running `test_loaders.py` and `test_chunkers.py` shows all test functions raise `NotImplementedError` — these are unimplemented stubs that pre-date this issue. They are not failures caused by my changes. The brief did not list these as tests to run or fix.

### What the Orchestrator Should Know

1. The `chunk_file` signature change (`text: str` → `content: str | bytes`, added `path: Path = None`) is backward-compatible: existing callers passing `text` as a positional string argument continue to work unchanged. No other caller of `chunk_file` exists in the current codebase outside `pipeline.py`.

2. The test stubs in `docs/backend/tests/unit/test_loaders.py` and `docs/backend/tests/unit/test_chunkers.py` include image-related test cases (`test_image_loader_returns_bytes`, `test_image_produces_exactly_one_chunk`, `test_image_chunk_carries_file_path_and_no_content`) that are still `raise NotImplementedError` stubs. A separate issue should implement these conftest fixtures and test bodies — the logic they should test now exists.

3. `embed_image` requires `OPENROUTER_API_KEY` at runtime. The function cannot be integration-tested without it. End-to-end image ingestion testing will need an environment with a valid key.

### What the Next Worker Needs

**Issue 8 (POST /chat) and Issue 9 (CLI) — image chunk handling in query results:**

- Image chunks have `page_content == ""`. Any code that uses the chunk's text content for answer generation or display will get an empty string. The chat handler must check `metadata["file_type"] == "image"` and handle it differently (e.g., cite the filename without quoting chunk text, or skip text-based relevance scoring on the content field).
- The `file_path` field in metadata is an absolute path to the image on disk. The chat UI could use this to display the image inline or provide a download link.
- Image chunks produce a single embedding via `embed_image`, not via `embed_texts`. The retrieval path (hybrid or vector) is unaffected since all chunks are stored in ChromaDB the same way — only the ingestion path differs.

### Blockers
None.
