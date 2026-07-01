### Status
COMPLETE

### What I Built

**`backend/ingestion/loaders.py`** — 2 additions:
- Added `load_md(path: Path) -> str` function (lines 29–31): reads the file with UTF-8 encoding, returning raw text with heading markers intact.
- Added `.md` branch to `load_file` dispatch (line 39–40): `elif suffix == ".md": return load_md(path)`. Updated the dispatch docstring to include `.md`.

**`backend/ingestion/chunkers.py`** — 3 additions:
- Added `MarkdownHeaderTextSplitter` to the import line (line 9).
- Added `chunk_md(text: str, filename: str) -> list[Document]` function (lines 27–37): splits on `#`, `##`, `###` boundaries, then stamps every resulting Document with `filename` and `file_type="markdown"` in metadata.
- Added `"markdown"` branch to `chunk_file` dispatch (lines 48–49): `elif file_type == "markdown": return chunk_md(text, filename)`. Updated the dispatch docstring to include `'markdown'`.

No other files were touched.

### Test Results

Ran scratch test from the brief verbatim (`python3 scratch_test.py` from `/workspace`):

```
Chunk count: 3
  metadata: {'h1': 'Section One', 'filename': 'test.md', 'file_type': 'markdown'}, content: Content about section one.
  metadata: {'h1': 'Section One', 'h2': 'Section Two', 'filename': 'test.md', 'file_type': 'markdown'}, content: Content about section two.
  metadata: {'h1': 'Section One', 'h2': 'Section Three', 'filename': 'test.md', 'file_type': 'markdown'}, content: Content about section three.
All assertions passed
```

- PASS: 3 sections produced 3 chunks (no chunk spans two sections)
- PASS: All chunks carry `filename == "test.md"`
- PASS: All chunks carry `file_type == "markdown"`
- PASS: All chunks are `langchain_core.documents.Document` objects with `page_content` set to section body text
- PASS: Headings preserved in raw text (`"# Section One" in text`)

### What the Orchestrator Should Know

- `MarkdownHeaderTextSplitter` preserves ancestor heading keys in metadata (e.g., a `##` section also gets the `h1` key from the parent). This is the library's default behaviour and is harmless — `filename` and `file_type` are always present regardless.
- Assumption: the brief says `file_type="markdown"` is the string the pipeline will pass to `chunk_file`. Issue 5 (pipeline worker) must ensure it calls `chunk_file(text, filename, "markdown")` and not `"md"`.

### What the Next Worker Needs

Issue 4 (image ingestion) can follow the same pattern:
- Add `load_<ext>(path) -> str` to `loaders.py` and a branch in `load_file`.
- Add `chunk_<type>(text, filename) -> list[Document]` to `chunkers.py` and a branch in `chunk_file`.
- The `chunk_file` signature `(text: str, filename: str, file_type: str) -> list[Document]` remains unchanged and continues to dispatch on `file_type`.

Issue 5 (pipeline integration) needs to know:
- `load_file` now handles `.md` natively — no changes needed to call it.
- `chunk_file` dispatches on `file_type == "markdown"` (not `"md"`).
- Add `".md"` to `SUPPORTED_EXTENSIONS` in `pipeline.py` and pass `file_type="markdown"` when invoking `chunk_file` for `.md` files.

### Blockers
None.
