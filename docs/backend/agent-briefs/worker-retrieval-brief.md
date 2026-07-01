# Worker Brief — Issue 6: BM25 Index and Hybrid Retrieval with RRF Fusion

**Working directory:** `/workspace`
**Issue:** Issue 6 (from docs/backend/issues.md)
**Your report goes to:** `docs/backend/agent-reports/worker-retrieval-report.md`

---

## Context

Issue 2 built ChromaDB vector storage and an embedding client. You are adding the second retrieval path: keyword-based BM25 search. You then wire both paths together with RRF fusion into a `HybridRetriever`.

You create three things:
1. A new method on `ChromaStore` to fetch all text chunks (needed for BM25 index building)
2. `backend/retrieval/bm25.py` — BM25 index class
3. `backend/retrieval/hybrid.py` — hybrid retriever that fuses BM25 + vector search with RRF

**Do NOT touch `server.py`** — the BM25 initialization in the server lifespan will be wired by Issue 7's worker (Round 3b). Your job is to build the retrieval logic so it can be plugged in.

---

## pip Environment

```bash
pip install -r /workspace/requirements.txt --user --break-system-packages
```
Use `python3 -m pytest`. PATH includes `/home/claude/.local/bin`.

---

## Existing Interfaces You Build On

**`backend/embeddings/store.py`** — `ChromaStore` class:
```python
class ChromaStore:
    def __init__(self, path: str): ...
    def insert_chunks(self, chunks: list[Document], embeddings: list[list[float]]) -> None: ...
    def delete_by_filename(self, filename: str) -> None: ...
    def query(self, embedding: list[float], top_k: int = 3) -> list[Document]: ...
    def get_unique_filenames(self) -> list[str]: ...
```

**`backend/embeddings/embedder.py`** — `EmbeddingClient`:
```python
class EmbeddingClient:
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
    # embed_image will be added by Issue 4
```

---

## Files to Create / Modify

### 1. `backend/embeddings/store.py` (MODIFY — add one method)

Add `get_all_text_chunks()` to `ChromaStore`. This is the only change to store.py — all existing methods stay unchanged.

```python
def get_all_text_chunks(self) -> list[Document]:
    """
    Return all stored chunks whose file_type is NOT 'image'.
    Used to build the BM25 index from text content only.
    """
    result = self._collection.get(include=["documents", "metadatas"])
    docs = []
    for doc, meta in zip(result["documents"], result["metadatas"]):
        if meta.get("file_type") != "image":
            docs.append(Document(page_content=doc, metadata=meta))
    return docs
```

Note: `result["documents"]` is a list of strings (the page_content), `result["metadatas"]` is a list of dicts. Handle the empty-collection case: `result["documents"]` will be an empty list, so the zip produces nothing — no special case needed.

### 2. `backend/retrieval/bm25.py` (NEW)

```python
"""
BM25 keyword index for docuFetch.

Builds an in-memory BM25 index from text chunks stored in ChromaDB.
Image chunks are excluded — they have no text content to keyword-match.
The index can be rebuilt from scratch without restarting the server.
"""
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi


class BM25Index:
    """In-memory BM25 index over text chunks."""

    def __init__(self, documents: list[Document]):
        """
        Build the BM25 index from a list of Documents.
        Tokenises each document's page_content by whitespace splitting.
        Image chunks (file_type='image') are excluded even if passed in.
        """
        self._docs = [d for d in documents if d.metadata.get("file_type") != "image"]
        tokenised = [d.page_content.lower().split() for d in self._docs]
        self._index = BM25Okapi(tokenised) if tokenised else None

    def query(self, query_text: str, top_k: int = 5) -> list[Document]:
        """
        Return up to top_k Documents ranked by BM25 score for query_text.
        Returns an empty list if the index is empty.
        """
        if self._index is None or not self._docs:
            return []
        tokens = query_text.lower().split()
        scores = self._index.get_scores(tokens)
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [self._docs[i] for i in ranked[:top_k]]
```

### 3. `backend/retrieval/hybrid.py` (NEW)

```python
"""
Hybrid retriever for docuFetch.

Runs BM25 keyword search and ChromaDB vector similarity search in parallel,
then fuses the two ranked result lists using Reciprocal Rank Fusion (RRF).
Returns the top-K fused chunks.
"""
from langchain_core.documents import Document

from backend.retrieval.bm25 import BM25Index
from backend.embeddings.store import ChromaStore
from backend.embeddings.embedder import EmbeddingClient


def _rrf_fuse(list_a: list[Document], list_b: list[Document], final_k: int = 3) -> list[Document]:
    """
    Fuse two ranked Document lists using Reciprocal Rank Fusion.

    Score formula: sum of 1/(rank+60) across all lists where the document appears.
    Deduplication key: (filename, first 100 chars of page_content).
    Returns at most final_k Documents sorted by descending fused score.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for rank, doc in enumerate(list_a, start=1):
        key = doc.metadata.get("filename", "") + doc.page_content[:100]
        scores[key] = scores.get(key, 0.0) + 1.0 / (rank + 60)
        doc_map[key] = doc

    for rank, doc in enumerate(list_b, start=1):
        key = doc.metadata.get("filename", "") + doc.page_content[:100]
        scores[key] = scores.get(key, 0.0) + 1.0 / (rank + 60)
        doc_map[key] = doc

    sorted_keys = sorted(scores, key=lambda k: scores[k], reverse=True)
    return [doc_map[k] for k in sorted_keys[:final_k]]


class HybridRetriever:
    """Combines BM25 and vector similarity retrieval via RRF fusion."""

    def __init__(self, bm25_index: BM25Index, chroma_store: ChromaStore, embedder: EmbeddingClient):
        """
        Initialise the hybrid retriever with both retrieval backends and the embedder.
        bm25_index can be rebuilt and replaced via rebuild_bm25().
        """
        self._bm25 = bm25_index
        self._store = chroma_store
        self._embedder = embedder

    def rebuild_bm25(self, documents: list[Document]) -> None:
        """
        Replace the BM25 index with a freshly built one from documents.
        Call this after each ingestion run to keep the index current.
        """
        self._bm25 = BM25Index(documents)

    def retrieve(self, query: str, n_per_retriever: int = 5, final_k: int = 3) -> list[Document]:
        """
        Run BM25 and vector search, fuse results with RRF, return top final_k chunks.

        BM25 searches text chunks only (images excluded at index build time).
        Vector search includes all chunks (text and image).
        """
        bm25_results = self._bm25.query(query, top_k=n_per_retriever)
        query_embedding = self._embedder.embed_texts([query])[0]
        vector_results = self._store.query(query_embedding, top_k=n_per_retriever)
        return _rrf_fuse(bm25_results, vector_results, final_k=final_k)
```

---

## Acceptance Criteria (verify all before reporting done)

- [ ] A keyword query returns up to 5 BM25 candidates from text chunks only (no image chunks in BM25 results)
- [ ] A semantic query returns up to 5 vector search candidates
- [ ] The fused result contains at most 3 chunks after RRF re-ranking and deduplication
- [ ] A term that appears verbatim in a document ranks higher after hybrid fusion than vector search alone
- [ ] BM25 index document count equals the number of text-only chunks (images excluded)

---

## How to Verify (no API keys needed for BM25 unit test)

Write a scratch test for the BM25 and RRF logic:
```python
from langchain_core.documents import Document
from backend.retrieval.bm25 import BM25Index
from backend.retrieval.hybrid import _rrf_fuse

# BM25 test
docs = [
    Document(page_content="the quick brown fox jumps", metadata={"filename": "a.txt", "file_type": "txt"}),
    Document(page_content="a lazy dog sat in the sun", metadata={"filename": "b.txt", "file_type": "txt"}),
    Document(page_content="foxes are cunning animals", metadata={"filename": "c.txt", "file_type": "txt"}),
    Document(page_content="", metadata={"filename": "img.jpg", "file_type": "image"}),  # should be excluded
]

idx = BM25Index(docs)
print(f"BM25 index size: {len(idx._docs)} (should be 3, not 4)")
assert len(idx._docs) == 3, "Image chunks must be excluded"

results = idx.query("fox", top_k=5)
print(f"BM25 results for 'fox': {[d.metadata['filename'] for d in results]}")
assert results[0].metadata["filename"] in ("a.txt", "c.txt"), "fox-related doc should rank first"
print("BM25 tests passed")

# RRF test
list_a = [
    Document(page_content="shared doc", metadata={"filename": "shared.txt"}),
    Document(page_content="only in a", metadata={"filename": "a_only.txt"}),
]
list_b = [
    Document(page_content="only in b", metadata={"filename": "b_only.txt"}),
    Document(page_content="shared doc", metadata={"filename": "shared.txt"}),
]
fused = _rrf_fuse(list_a, list_b, final_k=3)
print(f"RRF top result: {fused[0].metadata['filename']} (should be shared.txt)")
assert fused[0].metadata["filename"] == "shared.txt", "Shared doc should rank first"
print("RRF tests passed")
```

Run: `cd /workspace && python3 scratch_retrieval.py`

---

## Coding Standards

- Every function and method must have a docstring
- Every new file must have a module-level docstring
- The `_rrf_fuse` function is module-private (underscore prefix) since callers use `HybridRetriever.retrieve`

---

## What to Write in Your Report

Write `docs/backend/agent-reports/worker-retrieval-report.md` with:
1. Status: DONE or FAILED
2. Files created/modified (include line counts)
3. Verification output (paste scratch test results)
4. Interface summary for Issue 7 worker:
   - Exact `HybridRetriever` constructor signature
   - Exact `HybridRetriever.retrieve()` signature and return type
   - Exact `HybridRetriever.rebuild_bm25()` signature
   - Where to get the ChromaStore to build the BM25 from (`get_all_text_chunks()`)
5. Any deviations and why
