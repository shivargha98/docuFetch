### Status
COMPLETE

### What I Built

**Modified:**
- `/workspace/backend/embeddings/store.py` — added `get_all_text_chunks()` method (lines 64–76, +13 lines)

**Created:**
- `/workspace/backend/retrieval/bm25.py` — 38 lines
- `/workspace/backend/retrieval/hybrid.py` — 66 lines

**Scratch test (temporary):**
- `/workspace/scratch_retrieval.py` — 39 lines (can be deleted after review)

### Test Results

Ran: `python3 scratch_retrieval.py` from `/workspace`

```
BM25 index size: 3 (should be 3, not 4)
BM25 results for 'fox': ['a.txt', 'b.txt', 'c.txt']
BM25 tests passed
RRF top result: shared.txt (should be shared.txt)
RRF tests passed
All scratch tests passed.
```

All acceptance criteria verified:
- **Image exclusion:** BM25 index built from 3 text docs, not 4 (image chunk excluded) — PASS
- **BM25 top result:** a.txt (contains "fox" verbatim) ranked first — PASS
- **RRF deduplication:** shared.txt (appears in both lists) ranked first — PASS
- **fused result cap:** `_rrf_fuse(..., final_k=3)` returns at most 3 documents — PASS
- **BM25 doc count == text-only count:** `len(idx._docs) == 3` assertion passed — PASS

Note on BM25 ranking order for "fox": a.txt ranked 1st (contains "fox" exactly), b.txt ranked 2nd, c.txt 3rd. c.txt contains "foxes" not "fox" — BM25 has no stemming, so "fox" and "foxes" are distinct tokens. The assertion only requires rank-1 to be in ("a.txt", "c.txt"), which a.txt satisfies.

### What the Orchestrator Should Know

- `rank_bm25` was not installed at task start; it was added to `requirements.txt` already and installed via `python3 -m pip install -r requirements.txt --user --break-system-packages`.
- The `backend/retrieval/` directory and its `__init__.py` already existed (likely from scaffold work).
- BM25 has no stemming — "fox" and "foxes" are treated as different tokens. This is expected behaviour and consistent with the brief's design.

### What the Next Worker Needs

**Issue 7 / Integration worker:** Here are the exact interfaces to wire into `server.py`:

```python
# Import paths
from backend.retrieval.bm25 import BM25Index
from backend.retrieval.hybrid import HybridRetriever

# Constructor
HybridRetriever(
    bm25_index: BM25Index,
    chroma_store: ChromaStore,
    embedder: EmbeddingClient,
)

# Retrieve method
HybridRetriever.retrieve(
    query: str,
    n_per_retriever: int = 5,
    final_k: int = 3,
) -> list[Document]

# Rebuild BM25 after ingestion
HybridRetriever.rebuild_bm25(documents: list[Document]) -> None

# How to get documents for BM25 index build (from ChromaStore):
chroma_store.get_all_text_chunks() -> list[Document]

# Typical server lifespan initialisation pattern:
text_chunks = chroma_store.get_all_text_chunks()
bm25_index = BM25Index(text_chunks)
retriever = HybridRetriever(bm25_index, chroma_store, embedder)

# After each ingestion run:
retriever.rebuild_bm25(chroma_store.get_all_text_chunks())
```

### Blockers
None.
