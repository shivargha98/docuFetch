# Worker Brief — Issue 3: Markdown Ingestion with Header-Aware Chunking

**Working directory:** `/workspace`
**Issue:** Issue 3 (from docs/backend/issues.md)
**Your report goes to:** `docs/backend/agent-reports/worker-markdown-ingestion-report.md`

---

## Context

Issue 2 built TXT and PDF ingestion. You are extending it for Markdown files. You touch exactly two files: `backend/ingestion/loaders.py` and `backend/ingestion/chunkers.py`. Do not touch pipeline.py, routes.py, server.py, or any other file — another worker is modifying those concurrently.

The pipeline (`pipeline.py`) will be updated by Issue 5's worker to add `.md` to `SUPPORTED_EXTENSIONS`. Your job is only to make the loader and chunker ready for when the pipeline calls them with a markdown file.

---

## pip Environment

```bash
pip install -r /workspace/requirements.txt --user --break-system-packages
```
Use `python3 -m pytest` (not `pytest` directly). PATH includes `/home/claude/.local/bin`.

---

## Existing Interface to Extend

Current `backend/ingestion/loaders.py`:
```python
class UnsupportedFileTypeError(Exception): ...

def load_txt(path: Path) -> str: ...
def load_pdf(path: Path) -> str: ...
def load_file(path: Path) -> str:  # dispatch: .txt → load_txt, .pdf → load_pdf, else raises UnsupportedFileTypeError
```

Current `backend/ingestion/chunkers.py`:
```python
def chunk_text(text: str, filename: str, file_type: str) -> list[Document]: ...
def chunk_file(text: str, filename: str, file_type: str) -> list[Document]:
    # dispatch: "txt" or "pdf" → chunk_text, else raises ValueError
```

---

## Changes to Make

### 1. `backend/ingestion/loaders.py` — add `load_md`

Add this function:
```python
def load_md(path: Path) -> str:
    """Load a Markdown file and return its raw text content with heading markers preserved."""
    return path.read_text(encoding="utf-8")
```

Add `.md` to the `load_file` dispatch:
```python
elif suffix == ".md":
    return load_md(path)
```

That's it for loaders.py.

### 2. `backend/ingestion/chunkers.py` — add `chunk_md`

Add this function using `MarkdownHeaderTextSplitter`:
```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

def chunk_md(text: str, filename: str) -> list[Document]:
    """
    Split Markdown text at #, ##, and ### header boundaries.
    Each chunk corresponds to exactly one section. Every chunk carries
    filename and file_type='markdown' in its metadata.
    """
    headers_to_split_on = [("#", "h1"), ("##", "h2"), ("###", "h3")]
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    docs = splitter.split_text(text)
    for doc in docs:
        doc.metadata["filename"] = filename
        doc.metadata["file_type"] = "markdown"
    return docs
```

Add `"markdown"` to the `chunk_file` dispatch:
```python
elif file_type == "markdown":
    return chunk_md(text, filename)
```

---

## Acceptance Criteria (verify all before reporting done)

- [ ] A Markdown file with multiple `##` sections produces one chunk per section; no chunk spans two sections
- [ ] Each Markdown chunk carries `filename` and `file_type: "markdown"` in its metadata
- [ ] Markdown chunks are `langchain_core.documents.Document` objects with `page_content` set to the section content

---

## How to Verify (without running the full server)

Write a quick inline test in a scratch file:

```python
# scratch test
from pathlib import Path
import tempfile, os

with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
    f.write("# Section One\n\nContent about section one.\n\n## Section Two\n\nContent about section two.\n\n## Section Three\n\nContent about section three.\n")
    path = Path(f.name)

from backend.ingestion.loaders import load_md, load_file
from backend.ingestion.chunkers import chunk_md, chunk_file

text = load_file(path)
assert "# Section One" in text, "Headings must be preserved"

chunks = chunk_file(text, "test.md", "markdown")
print(f"Chunk count: {len(chunks)}")
for c in chunks:
    print(f"  metadata: {c.metadata}, content: {c.page_content[:50]}")

assert len(chunks) >= 2, "Should have multiple chunks for multiple sections"
assert all(c.metadata["filename"] == "test.md" for c in chunks)
assert all(c.metadata["file_type"] == "markdown" for c in chunks)
print("All assertions passed")
os.unlink(path)
```

Run: `cd /workspace && python3 scratch_test.py`

Remove the scratch file after verifying.

---

## Coding Standards

- Add a docstring to every new function
- Do not remove or change existing functions — only add
- The module-level docstring at the top of each file already exists; update it only if your addition warrants it (it probably does not)

---

## What to Write in Your Report

Write `docs/backend/agent-reports/worker-markdown-ingestion-report.md` with:
1. Status: DONE or FAILED
2. Exact lines added to loaders.py and chunkers.py
3. Verification output (paste the scratch test output)
4. Any deviations and why
5. What Issue 4 (image ingestion) needs to know about the interfaces you left in place
