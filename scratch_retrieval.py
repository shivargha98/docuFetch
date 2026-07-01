"""Scratch test for BM25 and RRF logic — no API keys required."""
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
print("All scratch tests passed.")
