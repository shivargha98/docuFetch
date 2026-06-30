"""
Integration tests for the end-to-end ingestion pipeline.

Covers: TXT, PDF, Markdown, and image file ingestion into a real ChromaDB
collection; chunk deduplication on re-ingestion; and re-ingestion of a
modified file replacing old chunks.

Uses real file I/O, real ChromaDB (temp dir), and the OpenRouter embedding
client. Set OPENROUTER_API_KEY in the test environment or skip with a marker.
"""

import pytest


def test_txt_file_ingested_end_to_end(tmp_watch_folder, sample_txt_file, chromadb_collection):
    """
    Given a TXT file in the watch folder and a real ChromaDB instance,
    when the full ingestion pipeline runs for that file,
    at least one chunk should exist in ChromaDB for that filename,
    each chunk should carry filename and file_type='txt' metadata,
    and running ingestion again for the same unchanged file should produce
    no duplicate chunks.

    Source: Issue 2 — criteria 1, 3, 4 | Feature: Structure-Aware Chunkers
    """
    raise NotImplementedError


def test_pdf_file_ingested_end_to_end(tmp_watch_folder, sample_pdf_file, chromadb_collection):
    """
    Given a PDF file in the watch folder,
    when the full ingestion pipeline runs,
    at least one chunk should exist in ChromaDB with filename and
    file_type='pdf' metadata.

    Source: Issue 2 — criteria 1, 3, 4
    """
    raise NotImplementedError


def test_markdown_chunks_respect_header_boundaries(tmp_watch_folder, sample_md_file, chromadb_collection):
    """
    Given a Markdown file with three ## sections,
    when the Markdown ingestion pipeline runs,
    ChromaDB should contain exactly three chunks for the file and each
    chunk's content should correspond to one section only.

    Source: Issue 3 — criteria 1, 2 | Feature: Structure-Aware Chunkers
    """
    raise NotImplementedError


def test_image_ingested_as_single_chunk_with_file_path(tmp_watch_folder, sample_image_file, chromadb_collection):
    """
    Given a JPEG file in the watch folder,
    when the image ingestion pipeline runs,
    exactly one chunk should exist in ChromaDB for that filename, the chunk's
    metadata should contain file_path and file_type='image', and the content
    field should be empty or absent.

    Source: Issue 4 — criteria 1, 2 | Feature: Structure-Aware Chunkers
    """
    raise NotImplementedError


def test_modified_file_replaces_old_chunks(tmp_watch_folder, hash_store_path, chromadb_collection):
    """
    Given a TXT file that has been ingested (chunks in ChromaDB, hash in store),
    when the file's content changes (new hash) and the scanner detects the
    modification and re-runs ingestion,
    the old chunks should be absent from ChromaDB, new chunks should be
    present, and no duplicate chunks for that filename should exist.

    Source: Feature: File Change Detection — criterion 2 | Issue 5 — criterion 2
    """
    raise NotImplementedError
