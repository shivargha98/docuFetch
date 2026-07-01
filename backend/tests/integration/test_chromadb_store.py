"""Integration tests for ChromaDB store operations."""
import pytest
from langchain_core.documents import Document
from backend.embeddings.store import ChromaStore


def test_insert_text_chunk_and_retrieve_by_vector(chromadb_store):
    chunk = Document(page_content="hello world test content", metadata={"filename": "test.txt", "file_type": "txt"})
    dummy_embedding = [0.1] * 2048
    chromadb_store.insert_chunks([chunk], [dummy_embedding])
    results = chromadb_store.query(dummy_embedding, top_k=1)
    assert len(results) == 1
    assert results[0].metadata["filename"] == "test.txt"
    assert results[0].metadata["file_type"] == "txt"


def test_insert_image_chunk_stores_file_path_without_content(chromadb_store):
    chunk = Document(page_content="", metadata={"filename": "photo.jpg", "file_type": "image", "file_path": "/watch/photo.jpg"})
    dummy_embedding = [0.2] * 2048
    chromadb_store.insert_chunks([chunk], [dummy_embedding])
    results = chromadb_store.query(dummy_embedding, top_k=1)
    assert len(results) == 1
    assert results[0].metadata["file_path"] == "/watch/photo.jpg"
    assert results[0].page_content == ""


def test_delete_by_filename_removes_all_associated_chunks(chromadb_store):
    chunks = [
        Document(page_content=f"chunk {i}", metadata={"filename": "report.pdf", "file_type": "pdf"})
        for i in range(3)
    ]
    other = Document(page_content="other doc", metadata={"filename": "other.txt", "file_type": "txt"})
    embeddings = [[float(i)] * 2048 for i in range(3)]
    other_emb = [0.9] * 2048
    chromadb_store.insert_chunks(chunks, embeddings)
    chromadb_store.insert_chunks([other], [other_emb])
    chromadb_store.delete_by_filename("report.pdf")
    filenames = chromadb_store.get_unique_filenames()
    assert "report.pdf" not in filenames
    assert "other.txt" in filenames


def test_vector_query_returns_at_most_k_results(chromadb_store):
    for i in range(10):
        chunk = Document(page_content=f"document number {i}", metadata={"filename": f"doc{i}.txt", "file_type": "txt"})
        emb = [float(i) / 10] * 2048
        chromadb_store.insert_chunks([chunk], [emb])
    query_emb = [0.5] * 2048
    results = chromadb_store.query(query_emb, top_k=3)
    assert len(results) <= 3
    for r in results:
        assert "filename" in r.metadata
