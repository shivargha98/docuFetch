# Worker Brief — Issue 4: Image Ingestion with Vision Embedding

**Working directory:** `/workspace`
**Issue:** Issue 4 (from docs/backend/issues.md)
**Your report goes to:** `docs/backend/agent-reports/worker-image-ingestion-report.md`

---

## Context

Issues 2 and 3 built TXT/PDF/Markdown ingestion. You are adding JPEG, JPG, and PNG support. You extend four existing files — no new files needed.

Files you own in this round:
- `backend/ingestion/loaders.py` — add `load_image`
- `backend/ingestion/chunkers.py` — add `chunk_image`
- `backend/embeddings/embedder.py` — add `embed_image`
- `backend/ingestion/pipeline.py` — add image extensions, add image branch in ingestion loop

Do NOT touch `server.py`, `routes.py`, `store.py`, `bm25.py`, `hybrid.py`, or any `graph/` files — another worker is using those concurrently.

---

## pip Environment

```bash
pip install -r /workspace/requirements.txt --user --break-system-packages
```
Use `python3 -m pytest`. PATH includes `/home/claude/.local/bin`.

---

## Existing Interfaces to Extend

**`backend/ingestion/loaders.py`** — current dispatch:
```python
def load_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt": return load_txt(path)
    elif suffix == ".pdf": return load_pdf(path)
    elif suffix == ".md": return load_md(path)
    else: raise UnsupportedFileTypeError(...)
```

**`backend/ingestion/chunkers.py`** — current dispatch:
```python
def chunk_file(text: str, filename: str, file_type: str) -> list[Document]:
    if file_type in ("txt", "pdf"): return chunk_text(text, filename, file_type)
    elif file_type == "markdown": return chunk_md(text, filename)
    raise ValueError(f"No chunker for file type: {file_type}")
```

**`backend/embeddings/embedder.py`** — current:
```python
class EmbeddingClient:
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
    # embed_image is added here by this issue
```

**`backend/ingestion/pipeline.py`** — current:
```python
SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".md"}
EXTENSION_TO_FILE_TYPE = {".txt": "txt", ".pdf": "pdf", ".md": "markdown"}

def run_ingestion(watch_folder, store, embedder, hash_store_path) -> dict:
    # handles scanner changes, calls load_file → chunk_file → embed_texts → insert_chunks
    # image branch NOT YET PRESENT — you add it
```

---

## Changes to Make

### 1. `backend/ingestion/loaders.py` — add `load_image`

Images are loaded as raw bytes via Pillow (which validates they are real images).

```python
from PIL import Image
import io

def load_image(path: Path) -> bytes:
    """
    Open and validate an image file using Pillow, then return its raw bytes.
    Raises UnsupportedFileTypeError if Pillow cannot open the file.
    """
    try:
        with Image.open(path) as img:
            img.verify()  # validates the image without fully loading it
    except Exception as exc:
        raise UnsupportedFileTypeError(f"Cannot load image at {path}: {exc}") from exc
    return path.read_bytes()
```

Add image suffixes to the `load_file` dispatch:
```python
elif suffix in (".jpg", ".jpeg", ".png"):
    return load_image(path)
```

Note: `load_file` currently returns `str`. For images it returns `bytes`. Change the return type hint to `str | bytes`.

### 2. `backend/ingestion/chunkers.py` — add `chunk_image`

Each image is one chunk. Content is empty; all info is in metadata.

```python
def chunk_image(path: Path, filename: str) -> list[Document]:
    """
    Return a single Document chunk for an image file.
    Content is empty; metadata contains filename, file_type, and file_path.
    """
    return [Document(
        page_content="",
        metadata={
            "filename": filename,
            "file_type": "image",
            "file_path": str(path.resolve()),
        }
    )]
```

The `chunk_file` dispatch currently takes `(text: str, filename: str, file_type: str)`. Images don't have text, so the signature cannot fit images cleanly. Add a separate dispatch check in `chunk_file` for the image case by checking for bytes or by changing the signature. The cleanest approach:

Change `chunk_file` to accept `content: str | bytes`:
```python
def chunk_file(content: str | bytes, filename: str, file_type: str, path: Path = None) -> list[Document]:
    """
    Dispatch to the appropriate chunker.
    For images, path must be provided to store file_path in metadata.
    """
    if file_type in ("txt", "pdf"):
        return chunk_text(content, filename, file_type)
    elif file_type == "markdown":
        return chunk_md(content, filename)
    elif file_type == "image":
        return chunk_image(path, filename)
    raise ValueError(f"No chunker for file type: {file_type}")
```

### 3. `backend/embeddings/embedder.py` — add `embed_image`

Images are sent to the same OpenRouter VL model as base64-encoded data URIs.

```python
import base64

_MIME_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}

def embed_image(self, image_bytes: bytes, suffix: str = ".jpg") -> list[float]:
    """
    Embed raw image bytes using the OpenRouter VL model.
    Returns one embedding vector of the same dimensionality as text embeddings (2048).
    suffix is the file extension used to determine the MIME type.
    """
    mime_type = _MIME_TYPES.get(suffix.lower(), "image/jpeg")
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = self._client.embeddings.create(
        model=OPENROUTER_EMBED_MODEL,
        input=[{
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{b64}"}
        }],
        encoding_format="float",
    )
    return response.data[0].embedding
```

### 4. `backend/ingestion/pipeline.py` — add image extensions and image branch

**Change A — extend SUPPORTED_EXTENSIONS and EXTENSION_TO_FILE_TYPE:**
```python
SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".md", ".jpg", ".jpeg", ".png"}

EXTENSION_TO_FILE_TYPE = {
    ".txt": "txt",
    ".pdf": "pdf",
    ".md": "markdown",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
}
```

**Change B — add image branch in the ingestion loop:**

Replace the existing ingestion loop body (which calls `load_file → chunk_file → embed_texts → insert_chunks`) with a branching version:

```python
for path in changes["new"] + changes["modified"]:
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        continue
    filename = path.name
    file_type = EXTENSION_TO_FILE_TYPE.get(path.suffix.lower(), path.suffix.lower().lstrip("."))
    store.delete_by_filename(filename)

    if file_type == "image":
        image_bytes = load_image(path)
        chunks = chunk_image(path, filename)
        embedding = embedder.embed_image(image_bytes, suffix=path.suffix)
        store.insert_chunks(chunks, [embedding])
    else:
        text = load_file(path)
        chunks = chunk_file(text, filename, file_type)
        embeddings = embedder.embed_texts([c.page_content for c in chunks])
        store.insert_chunks(chunks, embeddings)
```

Also update the import in pipeline.py to include `load_image`, `chunk_image`:
```python
from backend.ingestion.loaders import load_file, load_image, UnsupportedFileTypeError
from backend.ingestion.chunkers import chunk_file, chunk_image
```

---

## Acceptance Criteria (verify all before reporting done)

- [ ] A JPEG/JPG/PNG file in WATCH_FOLDER produces exactly one chunk in ChromaDB
- [ ] The chunk's metadata contains `file_path` (absolute path), `file_type: "image"`, and `filename`
- [ ] The chunk's content field is empty (`""`)
- [ ] After image ingestion, `GET /ingest/status` doc_count increments

---

## How to Verify (without running full server)

Write a scratch test that doesn't require API keys for the pure logic:

```python
import tempfile, os
from pathlib import Path
from PIL import Image

# Create a minimal test image
with tempfile.TemporaryDirectory() as tmpdir:
    img_path = Path(tmpdir) / "test.jpg"
    Image.new("RGB", (10, 10), color=(255, 0, 0)).save(img_path, "JPEG")
    
    from backend.ingestion.loaders import load_image
    from backend.ingestion.chunkers import chunk_image
    
    # Test loader
    raw_bytes = load_image(img_path)
    assert isinstance(raw_bytes, bytes) and len(raw_bytes) > 0
    print(f"Image bytes loaded: {len(raw_bytes)} bytes")
    
    # Test chunker
    chunks = chunk_image(img_path, "test.jpg")
    assert len(chunks) == 1
    assert chunks[0].page_content == ""
    assert chunks[0].metadata["file_type"] == "image"
    assert chunks[0].metadata["filename"] == "test.jpg"
    assert "test.jpg" in chunks[0].metadata["file_path"]
    print(f"Image chunk metadata: {chunks[0].metadata}")
    print("All image tests passed")
```

For `embed_image`, note that it requires `OPENROUTER_API_KEY`. If not available, verify the function exists and its signature is correct, and note this in your report.

---

## Coding Standards

- Add docstrings to all new functions
- Do not remove existing functions or change their signatures (only add/extend)
- `load_file` return type changes from `str` to `str | bytes` — update the type hint

---

## What to Write in Your Report

Write `docs/backend/agent-reports/worker-image-ingestion-report.md` with:
1. Status: DONE or FAILED
2. Files modified (every file, every change)
3. Verification output (paste scratch test output)
4. `embed_image` verification (actual API call result, or note if API key unavailable)
5. Any deviations and why
6. What Issue 8 (POST /chat) and Issue 9 (CLI) need to know about image chunk handling in query results
