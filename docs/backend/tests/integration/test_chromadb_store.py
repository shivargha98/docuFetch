"""
Integration tests for ChromaDB store operations.

Covers: insert text chunks with metadata, insert image chunks (file_path only),
delete by filename, and top-K vector query.

Uses a real ChromaDB collection backed by a temp directory — no mocking.
"""

import pytest


def test_insert_text_chunk_and_retrieve_by_vector(chromadb_collection):
    """
    Given an empty ChromaDB collection,
    when a text chunk with filename and file_type metadata is inserted and a
    vector query is run with a similar embedding,
    the inserted chunk should be returned and its metadata should match.

    Source: Feature: ChromaDB Store Operations — criterion 1
    """
    raise NotImplementedError


def test_insert_image_chunk_stores_file_path_without_content(chromadb_collection):
    """
    Given an empty ChromaDB collection,
    when an image chunk is inserted with file_path metadata and no content,
    the chunk should be retrievable by vector query, its metadata should
    contain file_path, and the content field should be empty or absent.

    Source: Feature: ChromaDB Store Operations — criterion 2
    """
    raise NotImplementedError


def test_delete_by_filename_removes_all_associated_chunks(chromadb_collection):
    """
    Given a ChromaDB collection containing three chunks all with
    filename='report.pdf' plus chunks from another file,
    when delete is called for filename='report.pdf',
    no chunks with that filename should remain and chunks from other
    filenames should be unaffected.

    Source: Feature: ChromaDB Store Operations — criterion 3
    """
    raise NotImplementedError


def test_vector_query_returns_at_most_k_results(chromadb_collection):
    """
    Given a ChromaDB collection containing 10 chunks,
    when a vector query is run with top_k=3,
    at most 3 chunks should be returned and every returned chunk should
    include its metadata dict.

    Source: Feature: ChromaDB Store Operations — criterion 4
    """
    raise NotImplementedError
