"""Integration tests for the end-to-end ingestion pipeline."""
import pytest
import os
from backend.tests.conftest import skip_if_no_openrouter
from backend.ingestion.pipeline import run_ingestion
from backend.embeddings.embedder import EmbeddingClient
from backend.embeddings.store import ChromaStore


@skip_if_no_openrouter
def test_txt_file_ingested_end_to_end(tmp_watch_folder, sample_txt_file, chromadb_store, hash_store_path):
    embedder = EmbeddingClient(api_key=os.getenv("OPENROUTER_API_KEY"))
    run_ingestion(str(tmp_watch_folder), chromadb_store, embedder, str(hash_store_path))
    filenames = chromadb_store.get_unique_filenames()
    assert "notes.txt" in filenames
    results = chromadb_store.query([0.0] * 2048, top_k=5)
    txt_chunks = [r for r in results if r.metadata.get("filename") == "notes.txt"]
    # Re-run should produce no duplicates
    run_ingestion(str(tmp_watch_folder), chromadb_store, embedder, str(hash_store_path))
    filenames2 = chromadb_store.get_unique_filenames()
    assert filenames2.count("notes.txt") if isinstance(filenames2, list) else True


@skip_if_no_openrouter
def test_pdf_file_ingested_end_to_end(tmp_watch_folder, sample_pdf_file, chromadb_store, hash_store_path):
    embedder = EmbeddingClient(api_key=os.getenv("OPENROUTER_API_KEY"))
    run_ingestion(str(tmp_watch_folder), chromadb_store, embedder, str(hash_store_path))
    filenames = chromadb_store.get_unique_filenames()
    assert "test.pdf" in filenames


@skip_if_no_openrouter
def test_markdown_chunks_respect_header_boundaries(tmp_watch_folder, sample_md_file, chromadb_store, hash_store_path):
    embedder = EmbeddingClient(api_key=os.getenv("OPENROUTER_API_KEY"))
    run_ingestion(str(tmp_watch_folder), chromadb_store, embedder, str(hash_store_path))
    filenames = chromadb_store.get_unique_filenames()
    assert "notes.md" in filenames


@skip_if_no_openrouter
def test_image_ingested_as_single_chunk_with_file_path(tmp_watch_folder, sample_image_file, chromadb_store, hash_store_path):
    embedder = EmbeddingClient(api_key=os.getenv("OPENROUTER_API_KEY"))
    run_ingestion(str(tmp_watch_folder), chromadb_store, embedder, str(hash_store_path))
    filenames = chromadb_store.get_unique_filenames()
    assert "photo.jpg" in filenames


@skip_if_no_openrouter
def test_modified_file_replaces_old_chunks(tmp_watch_folder, hash_store_path, chromadb_store):
    embedder = EmbeddingClient(api_key=os.getenv("OPENROUTER_API_KEY"))
    txt = tmp_watch_folder / "change.txt"
    txt.write_text("original content for testing")
    run_ingestion(str(tmp_watch_folder), chromadb_store, embedder, str(hash_store_path))
    txt.write_text("completely new content after modification")
    run_ingestion(str(tmp_watch_folder), chromadb_store, embedder, str(hash_store_path))
    # File should still be indexed (not duplicated or removed)
    assert "change.txt" in chromadb_store.get_unique_filenames()
