"""Unit tests for retrieval logic (no external services)."""
import pytest
from langchain_core.documents import Document
from backend.retrieval.bm25 import BM25Index
from backend.retrieval.hybrid import _rrf_fuse


def test_rrf_score_computed_correctly():
    doc_shared = Document(page_content="shared document content", metadata={"filename": "shared.txt"})
    doc_a_only = Document(page_content="only in list a", metadata={"filename": "a.txt"})
    doc_b_only = Document(page_content="only in list b", metadata={"filename": "b.txt"})
    list_a = [doc_a_only, doc_shared]  # shared is rank 2 in list A
    list_b = [doc_shared, doc_b_only]  # shared is rank 1 in list B
    fused = _rrf_fuse(list_a, list_b, final_k=3)
    # shared doc should rank first (appears in both lists)
    assert fused[0].metadata["filename"] == "shared.txt"


def test_bm25_ranks_by_keyword_relevance():
    docs = [
        Document(page_content="the weather is sunny today", metadata={"filename": "a.txt", "file_type": "txt"}),
        Document(page_content="foxes are cunning animals in the wild", metadata={"filename": "b.txt", "file_type": "txt"}),
        Document(page_content="the quick brown fox jumps over the lazy dog", metadata={"filename": "c.txt", "file_type": "txt"}),
    ]
    idx = BM25Index(docs)
    results = idx.query("fox", top_k=3)
    assert len(results) > 0
    # Documents containing "fox" should rank above the weather doc
    top_filenames = [r.metadata["filename"] for r in results[:2]]
    assert "a.txt" not in top_filenames or results[0].metadata["filename"] != "a.txt"
