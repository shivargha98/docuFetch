"""Integration tests for BM25 index and hybrid retrieval."""
import pytest
import os
from backend.tests.conftest import skip_if_no_openrouter
from langchain_core.documents import Document
from backend.retrieval.bm25 import BM25Index
from backend.retrieval.hybrid import HybridRetriever
from backend.embeddings.embedder import EmbeddingClient


def test_bm25_index_excludes_image_chunks(chromadb_store):
    text_chunk = Document(page_content="sample text content", metadata={"filename": "a.txt", "file_type": "txt"})
    img_chunk = Document(page_content="", metadata={"filename": "b.jpg", "file_type": "image"})
    chromadb_store.insert_chunks([text_chunk, img_chunk], [[0.1]*2048, [0.2]*2048])
    all_chunks = chromadb_store.get_all_text_chunks()
    idx = BM25Index(all_chunks)
    assert len(idx._docs) == 1
    results = idx.query("sample text")
    filenames = [r.metadata["filename"] for r in results]
    assert "b.jpg" not in filenames


def test_bm25_index_rebuild_includes_new_documents(chromadb_store):
    doc1 = Document(page_content="first document content", metadata={"filename": "first.txt", "file_type": "txt"})
    chromadb_store.insert_chunks([doc1], [[0.1]*2048])
    idx = BM25Index(chromadb_store.get_all_text_chunks())
    initial_results = idx.query("unique_keyword_xyz")
    assert len(initial_results) == 0 or "second.txt" not in [r.metadata["filename"] for r in initial_results]
    doc2 = Document(page_content="second document with unique_keyword_xyz", metadata={"filename": "second.txt", "file_type": "txt"})
    chromadb_store.insert_chunks([doc2], [[0.3]*2048])
    idx2 = BM25Index(chromadb_store.get_all_text_chunks())
    results2 = idx2.query("unique_keyword_xyz")
    assert any(r.metadata["filename"] == "second.txt" for r in results2)


def test_hybrid_retrieval_returns_at_most_three_chunks(chromadb_store):
    for i in range(12):
        doc = Document(page_content=f"document number {i} with various content", metadata={"filename": f"doc{i}.txt", "file_type": "txt"})
        chromadb_store.insert_chunks([doc], [[float(i)/12]*2048])
    idx = BM25Index(chromadb_store.get_all_text_chunks())

    class FakeEmbedder:
        def embed_texts(self, texts):
            return [[0.5]*2048]

    retriever = HybridRetriever(idx, chromadb_store, FakeEmbedder())
    results = retriever.retrieve("document content", final_k=3)
    assert len(results) <= 3
    for r in results:
        assert "filename" in r.metadata


def test_dual_relevant_document_ranks_first_after_rrf(chromadb_store):
    strong = Document(page_content="fox fox fox quick brown fox", metadata={"filename": "strong.txt", "file_type": "txt"})
    weak = Document(page_content="animals are interesting creatures", metadata={"filename": "weak.txt", "file_type": "txt"})
    chromadb_store.insert_chunks([strong, weak], [[0.9]*2048, [0.1]*2048])
    idx = BM25Index(chromadb_store.get_all_text_chunks())

    class FakeEmbedder:
        def embed_texts(self, texts):
            return [[0.9]*2048]  # high similarity to strong doc's embedding

    retriever = HybridRetriever(idx, chromadb_store, FakeEmbedder())
    results = retriever.retrieve("fox", final_k=2)
    assert len(results) >= 1
    assert results[0].metadata["filename"] == "strong.txt"
